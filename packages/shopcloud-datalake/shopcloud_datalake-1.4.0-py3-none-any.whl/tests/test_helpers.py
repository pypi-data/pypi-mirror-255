import argparse
import unittest
from datetime import datetime
from unittest.mock import Mock

from shopcloud_datalake import helpers


class TestBColors(unittest.TestCase):
    for color in helpers.bcolors.__dict__.keys():

        def test_color(self, color=color):
            print(color + "Test" + helpers.bcolors.ENDC)


class TestPipeline(unittest.TestCase):
    def test_init(self):
        pipeline = helpers.Pipeline("test_pipeline", "test_for")
        self.assertEqual(pipeline.name, "test_pipeline")
        self.assertEqual(pipeline._for, "test_for")
        self.assertTrue(pipeline.is_success)
        self.assertIsNone(pipeline.data)
        self.assertEqual(pipeline.steps, [])
        self.assertFalse(pipeline.raise_exceptio)

    def test_pipeline_as_dict(self):
        pipeline = helpers.Pipeline("test_pipeline", "test_for")
        data = pipeline.to_dict()
        self.assertEqual(data.get("name"), "test_pipeline")
        self.assertEqual(data.get("for"), "test_for")
        self.assertTrue(data.get("is_success"))

    def test_pipeline_as_repr(self):
        pipeline = helpers.Pipeline("test_pipeline", "test_for")
        data = pipeline.__repr__()
        self.assertIn("Pipeline", data)
        self.assertIn("test_pipeline", data)
        self.assertIn("test_for", data)
        self.assertIn("is_success", data)
        self.assertIn("steps", data)
        self.assertIn("data", data)

    def test_step_success(self):
        pipeline = helpers.Pipeline("test_pipeline", "test_for")
        pipeline.step("test_step", lambda p: "test_data")
        self.assertEqual(pipeline.data, "test_data")
        self.assertEqual(pipeline.steps, [{"name": "test_step", "is_success": True}])

    def test_step_success_then_failed(self):
        pipeline = helpers.Pipeline("test_pipeline", "test_for")
        pipeline.step("test_step_success", lambda p: "test_data")
        self.assertTrue(pipeline.is_success)
        pipeline.step("test_step_failed", lambda p: 1 / 0)
        self.assertFalse(pipeline.is_success)
        pipeline.step("test_step_success_2", lambda p: "test_data_2")
        self.assertEqual(len(pipeline.steps), 2)

    def test_step_failure(self):
        pipeline = helpers.Pipeline("test_pipeline", "test_for")
        pipeline.step("test_step", lambda p: 1 / 0)
        self.assertFalse(pipeline.is_success)
        self.assertEqual(len(pipeline.steps), 1)
        self.assertEqual(pipeline.steps[0]["name"], "test_step")
        self.assertFalse(pipeline.steps[0]["is_success"])
        self.assertIsInstance(pipeline.steps[0]["exception"], ZeroDivisionError)

    def test_step_failure_and_raise(self):
        pipeline = helpers.Pipeline("test_pipeline", "test_for", raise_exception=True)
        with self.assertRaises(ZeroDivisionError):
            pipeline.step("test_step", lambda p: 1 / 0)
        self.assertFalse(pipeline.is_success)
        self.assertEqual(len(pipeline.steps), 1)
        self.assertEqual(pipeline.steps[0]["name"], "test_step")
        self.assertFalse(pipeline.steps[0]["is_success"])
        self.assertIsInstance(pipeline.steps[0]["exception"], ZeroDivisionError)


class TestPipelineFromPipeline(unittest.TestCase):
    def setUp(self):
        self.pipeline = helpers.Pipeline(
            "test_pipeline", "test_for", raise_exception=True
        )
        self.pipeline.step("test_step", lambda p: "test_data")

    def test_from_pipeline(self):
        new_pipeline = helpers.Pipeline.create_from(self.pipeline)
        self.assertEqual(new_pipeline.name, self.pipeline.name)
        self.assertEqual(new_pipeline._for, self.pipeline._for)
        self.assertEqual(new_pipeline.raise_exceptio, self.pipeline.raise_exceptio)
        self.assertEqual(new_pipeline.is_success, self.pipeline.is_success)
        self.assertEqual(new_pipeline.data, self.pipeline.data)
        self.assertEqual(new_pipeline.steps, self.pipeline.steps)

    def test_from_pipeline_is_new_instance(self):
        new_pipeline = helpers.Pipeline.create_from(self.pipeline)
        self.assertNotEqual(id(new_pipeline), id(self.pipeline))

    def test_from_pipeline_does_not_affect_original(self):
        original_data = self.pipeline.data
        new_pipeline = helpers.Pipeline.create_from(self.pipeline)
        new_pipeline.data = "new_data"
        new_pipeline.partition = "PART"
        self.assertEqual(self.pipeline.data, original_data)
        self.assertEqual(new_pipeline.data, "new_data")
        self.assertEqual(new_pipeline.partition, "PART")


class TestFetchSecret(unittest.TestCase):
    def setUp(self):
        self.mock_hub = Mock()
        self.mock_hub.read.return_value = "secret"

    def test_fetch_secret_simulate(self):
        secret = helpers.fetch_secret(self.mock_hub, "test", simulate=True)
        self.assertEqual(secret, "secret")
        self.mock_hub.read.assert_not_called()

    def test_fetch_secret(self):
        secret = helpers.fetch_secret(self.mock_hub, "test")
        self.assertEqual(secret, "secret")
        self.mock_hub.read.assert_called_once_with("test")


class TestValidDate(unittest.TestCase):
    def test_valid_date(self):
        # Test with a valid date string
        self.assertEqual(
            helpers.valid_date("2022-01-01"),
            datetime.strptime("2022-01-01", "%Y-%m-%d").date(),
        )

        # Test with an invalid date string
        with self.assertRaises(argparse.ArgumentTypeError):
            helpers.valid_date("invalid-date")


if __name__ == "__main__":
    unittest.main()
