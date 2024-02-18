import time
import unittest
from python_workflow import Task, Step


class TestStep(unittest.TestCase):
    def test_start(self):
        class MyTask1(Task):
            def __init__(self, delay):
                super().__init__('my_task_1')
                self.delay = delay

            def run(self):
                time.sleep(self.delay)
                return 'It works 1!'

        class MyTask2(Task):
            def __init__(self, delay):
                super().__init__('my_task_2')
                self.delay = delay

            def run(self):
                time.sleep(self.delay)
                return 'It works 2!'

        step = Step('my_step', tasks=[
            MyTask1(1),
            MyTask1(1),
            MyTask2(2),
        ])
        step.start()

        self.assertEqual(step.name, 'my_step')
        self.assertEqual(
            step.value,
            {
                'my_task_1-0': 'It works 1!',
                'my_task_1-1': 'It works 1!',
                'my_task_2-2': 'It works 2!'
            }
        )
        task = step.tasks[0]
        self.assertEqual(round(task.duration), 1)
        task = step.tasks[1]
        self.assertEqual(round(task.duration), 1)
        task = step.tasks[2]
        self.assertEqual(round(task.duration), 2)
        self.assertEqual(round(step.duration), 4)


