from tasks.celery import celery_app


def call_task():
    print('inside_task')
    try:
        val = celery_app.send_task(
            'tasks.dpws_single_worker_tasks.test_task',
            ('There',),
            retry=True
        )
        print(val)
        print('task added')
    except Exception as e:
        raise
    return 4+4


if __name__ == '__main__':
    call_task()