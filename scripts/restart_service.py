import sys
import boto3
ecs = boto3.client('ecs')

def get_running_tasks():
    task_list = ecs.list_tasks(
        cluster=sys.argv[1],
        serviceName=sys.argv[2]
    )
    return task_list['taskArns']

def main():
    """
    Get the running task ID
    Initiate ECS service restart
    Wait for task to stop (indicating that a new task has taken over and deployment complete)
    """
    task_list = get_running_tasks()
    print(f'Restarting {sys.argv[1]}')
    restart = ecs.update_service(
        cluster=sys.argv[1],
        service=sys.argv[2],
        forceNewDeployment=True
    )
    waiter = ecs.get_waiter('tasks_stopped')
    print('Restart complete, waiting for service to stabilize')
    waiter.wait(
        cluster=sys.argv[1],
        tasks=task_list,
        WaiterConfig={
            'Delay': 10,
            'MaxAttempts': 60
        }
    )

if __name__ == '__main__':
    main()
