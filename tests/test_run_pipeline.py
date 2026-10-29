import json
import logging
import tempfile
import unittest
from pathlib import Path

import run as pipeline


class AutomatedRunnerTests(unittest.TestCase):
    @staticmethod
    def _temporary_directory():
        temporary_root = pipeline.ROOT / "tmp" / "tests"
        temporary_root.mkdir(parents=True, exist_ok=True)
        return tempfile.TemporaryDirectory(dir=temporary_root)

    def test_manifest_discovery_selects_source_and_mandros_pairs_only(self):
        manifest_path = pipeline.DEFAULT_DATA_DIR / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        jobs, skipped = pipeline.discover_jobs(pipeline.DEFAULT_DATA_DIR, manifest)
        manifest_jobs = [job for job in jobs if job.discovery_source == "data/manifest.json"]
        pairs = {(job.pdf_path.name, job.workbook_path.name) for job in manifest_jobs}
        self.assertEqual(len(manifest_jobs), 2)
        self.assertEqual(pairs, {("source.pdf", "mandros_input.xlsx")})
        self.assertTrue(any("manual" in item["path"].lower() for item in skipped))
        self.assertFalse(any("manual" in job.workbook_path.name.lower() for job in jobs))

    def test_run_directories_never_overwrite(self):
        with self._temporary_directory() as temporary:
            root = Path(temporary)
            first = pipeline.make_unique_run_dir(root)
            second = pipeline.make_unique_run_dir(root)
            self.assertNotEqual(first, second)
            self.assertTrue(first.is_dir())
            self.assertTrue(second.is_dir())

    def test_prebuilt_workbooks_are_hash_verified_before_copy(self):
        for fixture_id in pipeline.FIXTURE_BUILDERS:
            with self.subTest(fixture_id=fixture_id), self._temporary_directory() as temporary:
                destination = Path(temporary) / "corrected.xlsx"
                copied, mode = pipeline._verified_prebuilt_copy(fixture_id, destination)
                self.assertTrue(copied, mode)
                self.assertTrue(destination.is_file())

    def test_new_workbook_can_reuse_registered_source_pdf(self):
        with self._temporary_directory() as temporary:
            data = Path(temporary) / "data"
            study = data / "private" / "example"
            study.mkdir(parents=True)
            source = study / "source.pdf"
            registered = study / "mandros_input.xlsx"
            additional = study / "second_extraction.xlsx"
            source.write_bytes(b"pdf fixture")
            registered.write_bytes(b"xlsx fixture")
            additional.write_bytes(b"xlsx fixture 2")
            manifest = {
                "files": [
                    {"role": "source_pdf", "local_name": "example/source.pdf"},
                    {"role": "mandros_output", "local_name": "example/mandros_input.xlsx"},
                ]
            }
            jobs, _ = pipeline.discover_jobs(data, manifest)
            self.assertEqual(len(jobs), 2)
            self.assertIn(additional.resolve(), {job.workbook_path for job in jobs})

    def test_corrupted_pair_is_recorded_without_raising(self):
        with self._temporary_directory() as temporary:
            root = Path(temporary)
            pdf = root / "broken.pdf"
            workbook = root / "broken.xlsx"
            pdf.write_bytes(b"not a pdf")
            workbook.write_bytes(b"not an xlsx")
            run_dir = root / "outputs"
            run_dir.mkdir()
            logger = logging.getLogger("mandros_blind.test.corrupt")
            logger.handlers.clear()
            logger.addHandler(logging.NullHandler())
            result = pipeline.process_job(
                pipeline.StudyJob("broken", pdf, workbook, "test"),
                1,
                1,
                run_dir,
                {"dependencies": {}},
                logger,
            )
            self.assertEqual(result["status"], "failed")
            self.assertIn("error", result)
            self.assertTrue(any(run_dir.rglob("error.json")))

    def test_unchanged_registered_input_is_current(self):
        with self._temporary_directory() as temporary:
            root = Path(temporary)
            output_dir = root / "stable-output"
            output_dir.mkdir()
            (output_dir / "assessment.json").write_text("{}", encoding="utf-8")
            (output_dir / "study_corrected.xlsx").write_bytes(b"corrected workbook fixture")
            (output_dir / "job_manifest.json").write_text(
                json.dumps({"correction": {"status": "generated"}}), encoding="utf-8"
            )
            hashes = {"pdf": "a" * 64, "workbook": "b" * 64}
            entry = {
                "input_fingerprint": pipeline.input_fingerprint(hashes),
                "output_dir": str(output_dir),
                "status": "success",
            }
            self.assertTrue(pipeline.registry_entry_is_current(entry, hashes))
            changed = {"pdf": "a" * 64, "workbook": "c" * 64}
            self.assertFalse(pipeline.registry_entry_is_current(entry, changed))
            entry["status"] = "failed"
            self.assertFalse(pipeline.registry_entry_is_current(entry, hashes))

    def test_generic_dataset_uses_only_pdf_and_mandros_workbook(self):
        from app.generic_dataset import build_generic_dataset

        study_dir = pipeline.DEFAULT_DATA_DIR / "private" / "empagliflozin"
        pdf = study_dir / "empa vs placebo 2doses (RCT4).pdf"
        workbook = study_dir / "empa_vs_placebo_2doses__RCT4_extracted (7).xlsx"
        if not pdf.is_file() or not workbook.is_file():
            self.skipTest("generic PDF/XLSX fixture is unavailable")
        dataset = build_generic_dataset(pdf, workbook, {"issues": []})
        self.assertEqual(dataset["generation_mode"], "generic_pdf_mandros")
        self.assertEqual({item["document_type"] for item in dataset["document_inventory"]}, {
            "main_article_pdf", "mandros_extraction_xlsx"
        })
        self.assertFalse(any("manual" in item["document_name"].lower() for item in dataset["document_inventory"]))
        self.assertTrue(dataset["arms"])
        self.assertTrue(dataset["eligibility"])
        self.assertTrue(dataset["outcomes"])
        self.assertTrue(all("p_value" not in row for row in dataset["outcomes"]))
        self.assertTrue(all(row["meta_analysis_eligibility"] in {"READY", "REQUIRES_REVIEW", "NOT_POOLABLE"} for row in dataset["outcomes"]))


if __name__ == "__main__":
    unittest.main()
