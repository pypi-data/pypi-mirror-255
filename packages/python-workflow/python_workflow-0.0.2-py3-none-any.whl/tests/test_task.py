import logging
import unittest
from unittest.mock import patch, Mock
from python_workflow import Task


class TestTask(unittest.TestCase):
    def test_start(self):
        logging.basicConfig(level=logging.DEBUG)

        class MyTask(Task):
            def __init__(self):
                super().__init__('my_task', 'blablabla', lol=535)
                self.custom_value = None

            def run(self):
                return 'It works!'

            def on_complete(self):
                self.custom_value = 99

        mock_datetime = Mock(
            side_effect=[
                2,
                3
            ]
        )

        task = MyTask()
        self.assertEqual(task.custom_value, None)

        with patch('python_workflow.time', mock_datetime):
            task.start()

        self.assertEqual(task.name, 'my_task')
        self.assertEqual(task.duration, 1)
        self.assertEqual(task.start_at, 2)
        self.assertEqual(task.stop_at, 3)
        self.assertEqual(task.value, 'It works!')
        self.assertEqual(task._args, ('blablabla',))
        self.assertEqual(task._kwargs, {'lol': 535})
        self.assertEqual(task.custom_value, 99)

    def test_start_exception(self):

        class MyTask(Task):
            def __init__(self):
                super().__init__('my_task')
                self.custom_value = None

            def run(self):
                raise Exception('Error ! ')

            def on_error(self, *args, **kwargs):
                self.custom_value = 99

        mock_datetime = Mock(
            side_effect=[
                2,
                3
            ]
        )

        task = MyTask()
        self.assertEqual(task.custom_value, None)

        with patch('python_workflow.time', mock_datetime):
            task.start()

        self.assertEqual(task.name, 'my_task')
        self.assertEqual(task.duration, 1)
        self.assertEqual(task.start_at, 2)
        self.assertEqual(task.stop_at, 3)
        self.assertEqual(task.custom_value, 99)

