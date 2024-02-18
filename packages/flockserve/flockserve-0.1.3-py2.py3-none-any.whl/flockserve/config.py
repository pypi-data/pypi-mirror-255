import os
class FlockServeConfig():
    def __init__(self, parsed_args, **kwargs):
        """

        Must be supplied configs:
        skypilot_job_file:
        skypilot_servic_acc_keyfile:

        Other configs with default values:
        worker_capacity: 30
        worker_name_prefix: 'skypilot-worker'
        host: '0.0.0.0'
        port: 8000
        max_workers: 5

        """

        all_configs = ['skypilot_job_file', 'skypilot_servic_acc_keyfile', 'worker_capacity', 'worker_name_prefix',
                       'host', 'port', 'max_workers']


        # Default configs
        self.skypilot_job_file = parsed_args.job
        self.worker_capacity = 30
        self.worker_name_prefix = 'skypilot-worker'
        self.host = '0.0.0.0'
        self.port = 8000
        self.max_workers = 5

        # set the parsed env variables
        if parsed_args.envs:
            for key, value in parsed_args.envs.items():
                os.environ[key.upper()] = value

        # set the kwargs as config
        for key, value in kwargs.items():
            self.__setattr__(key, value)


        assert self.skypilot_job_file is not None, "skypilot_job_file must be supplied"

        # Set relevant environment variables as config
        for conf_item in all_configs:
            if os.environ.get(conf_item) is not None:
                self.__setattr__(conf_item.upper(), os.environ.get(conf_item))

