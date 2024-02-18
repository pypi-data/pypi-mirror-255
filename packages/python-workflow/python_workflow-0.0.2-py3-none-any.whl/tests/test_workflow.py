import unittest
from unittest.mock import patch, Mock
from python_workflow import Task, Step, Workflow


class TestWorkflow(unittest.TestCase):
    def test_start(self):
        class MyTask1(Task):
            def __init__(self):
                super().__init__('my_task_1')

            def run(self):
                return 'It works 1!'

        class MyTask2(Task):
            def __init__(self):
                super().__init__('my_task_2')

            def run(self):
                return 'It works 2!'

        mock_datetime = Mock(
            side_effect=[
                2,

                1,
                8, 9,
                10, 11,
                12, 14,
                17,

                20,
                28, 29,
                20, 21,
                22, 24,
                27,

                32
            ]
        )

        step1 = Step('my_step_1', tasks=[
            MyTask1(),
            MyTask1(),
            MyTask2(),
        ])
        step2 = Step('my_step_2', tasks=[
            MyTask1(),
            MyTask2(),
            MyTask2(),
        ])

        workflow = Workflow('my_workflow', steps=[step1, step2])
        with patch('python_workflow.time', mock_datetime):
            workflow.start()

        self.assertEqual(workflow.name, 'my_workflow')
        self.assertEqual(
            workflow.value,
            {
                'my_step_1-0': {
                    'my_task_1-0': 'It works 1!',
                    'my_task_1-1': 'It works 1!',
                    'my_task_2-2': 'It works 2!'
                },
                'my_step_2-1': {
                    'my_task_1-0': 'It works 1!',
                    'my_task_2-1': 'It works 2!',
                    'my_task_2-2': 'It works 2!'
                }
            }
        )

        step = workflow.steps[0]
        self.assertEqual(step.duration, 16)
        step = workflow.steps[1]
        self.assertEqual(step.duration, 7)
        self.assertEqual(workflow.duration, 30)

    def test_start_exception(self):
        class MyTask1(Task):
            def __init__(self):
                super().__init__('my_task_1')

            def run(self):
                raise Exception('Error')

        class MyTask2(Task):
            def __init__(self):
                super().__init__('my_task_2')

            def run(self):
                return 'It works 2!'

        step1 = Step('my_step_1', tasks=[
            MyTask1(),
            MyTask1(),
            MyTask2(),
        ])
        step2 = Step('my_step_2', tasks=[
            MyTask1(),
            MyTask2(),
            MyTask2(),
        ])

        workflow = Workflow('my_workflow', steps=[step1, step2])
        # with self.assertRaises(Exception) as e:
        #     workflow.start()
        #
        # self.assertEqual(workflow.name, 'my_workflow')
        # self.assertEqual(
        #     workflow.value,
        #     None
        # )

    def test_start_task_exception(self):
        class MyTask1(Task):
            def __init__(self):
                super().__init__('my_task_1')

            def run(self):
                raise Exception('Error')

            def on_error(self, *args, **kwargs):
                pass

        class MyTask2(Task):
            def __init__(self):
                super().__init__('my_task_2')

            def run(self):
                return 'It works 2!'

        step1 = Step('my_step_1', tasks=[
            MyTask1(),
            MyTask1(),
            MyTask2(),
        ])
        step2 = Step('my_step_2', tasks=[
            MyTask1(),
            MyTask2(),
            MyTask2(),
        ])

        workflow = Workflow('my_workflow', steps=[step1, step2])
        workflow.start()

        self.assertEqual(workflow.name, 'my_workflow')
        self.assertEqual(
            workflow.value,
            {
                'my_step_1-0': {
                    'my_task_1-0': None,
                    'my_task_1-1': None,
                    'my_task_2-2': 'It works 2!'
                },
                'my_step_2-1': {
                    'my_task_1-0': None,
                    'my_task_2-1': 'It works 2!',
                    'my_task_2-2': 'It works 2!'
                }
            }
        )

    def test_start_step_exception(self):
        class MyTask1(Task):
            def __init__(self):
                super().__init__('my_task_1')

            def run(self):
                raise Exception('Error')

        class MyTask2(Task):
            def __init__(self, *args, **kwargs):
                super().__init__('my_task_2', *args, **kwargs)

            def run(self):
                return 'It works 2!'

        class CustomStep(Step):
            def on_error(self, *args, **kwargs):
                pass

        step1 = Step(
            'my_step_1',
            tasks=[
                MyTask2('blabla', lol=635),
                MyTask2(),
                MyTask2(),
            ],
            lol=635
        )
        step2 = CustomStep('my_step_2', tasks=[
            MyTask1(),
            MyTask2(),
            MyTask2(),
        ])

        workflow = Workflow('my_workflow', steps=[step1, step2])
        workflow.start()

        # self.assertEqual(workflow.name, 'my_workflow')
        # self.assertEqual(
        #     workflow.value,
        #     {
        #         'my_step_1-0': {
        #             'my_task_2-0': 'It works 2!',
        #             'my_task_2-1': 'It works 2!',
        #             'my_task_2-2': 'It works 2!'
        #         },
        #         'my_step_2-1': None
        #     }
        # )
