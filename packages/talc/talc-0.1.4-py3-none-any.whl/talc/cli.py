import os
import csv as csvmod
import time
from typing import Literal
import click
import random
from talc.evals import Document, EvalsClient, TestCaseResponse, TestCaseWithRubric


talc_api_key: str | None = os.getenv("TALC_API_KEY", None)
talc_base_url: str | None = os.getenv(
    "TALC_BASE_URL", "http://evals-webserver-webapp.azurewebsites.net"
)


@click.group()
def evals():
    pass


@evals.command()
@click.option("--count", default=0, help="Number of cases to sample (0 for all).")
@click.option("--api_key", default=talc_api_key, help="Talc API key")
@click.option("--dataset", prompt="Dataset ID", help="The ID of the dataset to load.")
@click.option("--csv", default=None, help="Path to CSV file to save results to.")
def getdataset(count: int, dataset: str, api_key: str, csv: str) -> None:
    """Download or pretty print a test dataset from the server."""

    if api_key is None:
        raise click.UsageError(
            "No API key provided. Please set the TALC_API_KEY environment variable or provide the --api_key option."
        )

    client = EvalsClient(api_key, talc_base_url)
    data = client.get_dataset(dataset)

    if count == 0:
        count = len(dataset)

    random.shuffle(data)

    if csv is not None:
        with open(csv, "w", newline="") as csvfile:
            writer = csvmod.writer(csvfile)
            writer.writerow(["id", "content"])
            for case in data[:count]:
                writer.writerow([case.id, case.question])

    for case in data[:count]:
        print(case.question)


@evals.command()
@click.option("--api_key", default=talc_api_key, help="Talc API key")
@click.option(
    "--csv",
    prompt="Results CSV path",
    help="Path to CSV file to load results from. Columns should be 'id', 'result'. Header row is optional.",
)
@click.option("--print_failed", is_flag=True, help="Print the failed test cases.")
def grade(api_key: str, csv: str, print_failed: bool):
    """Grade a test run from a csv. Columns should be 'id', question, and 'result'. CSV should have a header row."""

    if api_key is None:
        raise click.UsageError(
            "No API key provided. Please set the TALC_API_KEY environment variable or provide the --api_key option."
        )

    client = EvalsClient(api_key, talc_base_url)

    with open(csv, newline="") as csvfile:
        reader = csvmod.reader(csvfile)

        results = [TestCaseResponse(id=row[0], response=row[2]) for row in reader]

    run_info = client.start_run()
    client.submit_responses(results)
    print("Submitted results. Beginning grading for run ID: " + run_info.id)

    while True:
        run_info = client.get_results()
        print(f"Progress: {run_info.completion_progress * 100}%")
        if run_info.completion_progress >= 1:
            print("\n=============================================")
            print("Grading complete.")
            print(f"Accuracy: {run_info.grade_accuracy}")
            print(f"Hallucination: {run_info.grade_hallucination}")
            print("=============================================\n")
            if print_failed and run_info.test_cases is not None:
                print("Failed cases:")
                for case in run_info.test_cases:
                    if case.grade_accuracy < 0.5:
                        print(
                            f"{case.id}: {case.question} -> {case.response} ({case.grade_reason})"
                        )
            break
        time.sleep(2)


@evals.command()
@click.option("--api_key", default=talc_api_key, help="Talc API key")
@click.option("--run_id", prompt="Run ID", help="The ID of the run to get results for.")
@click.option("--print_failed", is_flag=True, help="Print the failed test cases.")
def getresults(api_key: str, run_id: str, print_failed: bool):
    """Get the grades for a test run."""

    if api_key is None:
        raise click.UsageError(
            "No API key provided. Please set the TALC_API_KEY environment variable or provide the --api_key option."
        )

    client = EvalsClient(api_key, talc_base_url, run_id)
    run_info = client.get_results()

    assert run_info.grade_accuracy is not None
    assert run_info.grade_hallucination is not None

    print("\n=============================================")
    print("Grading complete.")
    print(f"Includes expected info: {round(run_info.grade_accuracy * 100,2)}%")
    print(
        f"Does not hallucinate additional info: {round(run_info.grade_hallucination * 100, 2)}%"
    )
    print("=============================================\n\n")

    if print_failed and run_info.test_cases is not None:
        for case in run_info.test_cases:
            if case.grade_accuracy < 0.5:
                print("==============Failed Case==============")
                print(f"Id: {case.id}")
                print(f"Question: {case.question}\n\n")
                print(f"Response: {case.response}\n\n")
                print(f"{case.grade_reason}\n\n")


@evals.command()
@click.option("--api_key", default=talc_api_key, help="Talc API key")
@click.option(
    "--csv",
    prompt="CSV path",
    help="Path to CSV file to upload. Columns should be 'question' and 'answer'. An optional source_text column can be included as well.",
)
@click.option("--name", prompt="Dataset name", help="The name of the dataset.")
def adddataset(api_key: str, csv: str, name: str):
    """Add a new dataset to the server."""

    if api_key is None:
        raise click.UsageError(
            "No API key provided. Please set the TALC_API_KEY environment variable or provide the --api_key option."
        )

    client = EvalsClient(api_key, talc_base_url)

    with open(csv, newline="") as csvfile:
        reader = csvmod.reader(csvfile)

        # Skip the first row. If it's not a header, we add it back later.
        header = next(reader, None)
        if header is None:
            raise click.UsageError("CSV file is empty.")

        dataset = [
            TestCaseWithRubric(
                question=row[0],
                expected_response=row[1],
                scenario_data={},
                id=None,
                source_content=([row[2]] if len(row) > 2 else []),
            )
            for row in reader
        ]

        # If the first row is not a header, add it back to the results.
        if header[0] != "question" or header[1] != "answer":
            dataset.append(
                TestCaseWithRubric(
                    question=header[0],
                    expected_response=header[1],
                    scenario_data={},
                    id=None,
                    source_content=([]),
                )
            )

    dataset_id = client.upload_dataset(name, dataset)
    print(f"Dataset created with ID: {dataset_id}")


@evals.command()
@click.option("--api_key", default=talc_api_key, help="Talc API key")
@click.option(
    "--csv",
    prompt="CSV path",
    help="Path to CSV file to upload. Columns should be 'question', 'expected_answer' and 'user_answer'. An optional source_text column can be included as well.",
)
@click.option(
    "--name",
    prompt="Dataset name",
    help="The name of the dataset.",
    default="Temp Dataset",
)
def upload_and_grade(api_key: str, csv: str, name: str):
    """Upload a CSV with questions, reference answers, and actual answers and grade it."""

    if api_key is None:
        raise click.UsageError(
            "No API key provided. Please set the TALC_API_KEY environment variable or provide the --api_key option."
        )

    client = EvalsClient(api_key, talc_base_url)

    with open(csv, newline="") as csvfile:
        reader = csvmod.reader(csvfile)

        # Skip the header row
        _ = next(reader, None)

        rows = [row for row in reader]

    dataset = [
        TestCaseWithRubric(
            question=row[0],
            expected_response=row[1],
            scenario_data={},
            id=None,
            source_content=([row[3]] if len(row) > 3 else []),
        )
        for row in rows
    ]

    dataset = client.upload_dataset(name, dataset)

    # Download the dataset to get the IDs
    data = client.get_dataset(dataset.id)

    # Map the IDs to the actual responses using the questions as a key

    id_map = {case.question: case.id for case in data}

    results = [
        TestCaseResponse(
            id=id_map[row[0]],
            response=row[2],
        )
        for row in rows
    ]

    # Create a run and submit the results
    run_info = client.start_run()
    client.submit_responses(results)
    print("Submitted results. Beginning grading for run ID: " + run_info.id)

    while True:
        run_info = client.get_results()
        print(f"Progress: {run_info.completion_progress * 100}%")
        if run_info.completion_progress >= 1:
            print("\n=============================================")
            print("Grading complete.")
            print(f"Accuracy: {run_info.grade_accuracy}")
            print(f"Hallucination: {run_info.grade_hallucination}")
            print("=============================================\n")
            break
        time.sleep(2)


@evals.command()
@click.option("--api_key", default=talc_api_key, help="Talc API key")
@click.option(
    "--file",
    prompt="Input folder, single file path, or URL.",
    help="Input folder, single file path, or URL. Multiple allowed.",
    multiple=True,
)
@click.option("--out", prompt="Output path", help="Path to save the output to.")
@click.option("--dataset_name", prompt="Dataset name", help="The name of the dataset.")
@click.option(
    "--sampling_mode",
    help="The sampling mode to use.",
    type=click.Choice(["main_file", "all_files", "random", "ranked"]),
    default="all_files",
)
@click.option(
    "--generation_modes",
    help="The generation modes to use.",
    type=click.Choice(["simple", "complex"]),
    default=["simple"],
    multiple=True,
)
def generate(
    api_key: str,
    file: list[str],
    out: str,
    dataset_name: str,
    sampling_mode: Literal["main_file", "all_files", "random", "ranked"],
    generation_modes: list[Literal["simple"] | Literal["complex"]],
):
    """Generate a dataset from a set of documents."""

    if api_key is None:
        raise click.UsageError(
            "No API key provided. Please set the TALC_API_KEY environment variable or provide the --api_key option."
        )

    client = EvalsClient(api_key, talc_base_url)

    documents: list[Document] = []

    # Figure out what kind of document each file is, and load it into a list of Document objects
    # If it's a URL, send the URL and the server will load it (might want to make this local in the future)
    # If it's a directory, load all the markdown files in the directory
    # If it's a file, load the file
    for f in file:
        if f.startswith("http") or f.startswith("https"):
            documents.append(Document(url=f, title=f))
        elif os.path.isdir(f):
            for root, _, files in os.walk(f):
                for path in files:
                    if path.endswith(".md"):
                        with open(os.path.join(root, path), "r") as f:
                            documents.append(Document(content=f.read(), title=f.name))
        elif os.path.isfile(f):
            with open(f, "r") as f:
                documents.append(Document(content=f.read(), title=f.name))

    dataset_job = client.start_generate_dataset(
        dataset_name, documents, sampling_mode, generation_modes
    )

    while True:
        dataset_job = client.get_dataset_creation_job(dataset_job.id)
        print("Generating: " + dataset_job.status)
        if dataset_job.status == "COMPLETE":
            break
        if dataset_job.status == "ERROR":
            print("Generation failed.")
            exit(1)
        time.sleep(2)

    dataset = client.get_dataset(dataset_job.dataset_id)

    with open(out, "w", newline="") as csvfile:
        writer = csvmod.writer(csvfile)
        writer.writerow(["id", "question"])
        for case in dataset:
            writer.writerow([case.id, case.question])

    print(f"Dataset created with ID: {dataset_job.dataset_id}")
    print(f"Dataset written to {out}")


def main():
    evals()
