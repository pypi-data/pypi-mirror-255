import mlflow


class SolAccUtil:

    @staticmethod
    def display_html(html_content):
        """
        Display HTML content in various environments.

        Args:
            html_content (str): The HTML content to be displayed.

        Returns:
            None
        """
        try:
            from dbruntime.display import displayHTML

            # Try to use Databricks' displayHTML if in Databricks environment
            displayHTML(html_content)
        except NameError:
            try:
                # If not in Databricks, try using IPython's display function, useful in Jupyter notebooks
                from IPython.core.display import display, HTML

                display(HTML(html_content))
            except ImportError:
                # As a last resort, just print the HTML. This won't render it, but at least shows the content.
                print(html_content)

    def __init__(
        self, project_name, data_path=None, base_path=None, project_data_paths=None
    ):
        """
        Initializes the SolAccUtil object.

        Args:
            project_name (str): The name of the project.
            data_path (str, optional): The data path for the project. Defaults to None.
            base_path (str, optional): The base path for the project. Defaults to None.
        """
        user = (
            dbutils.notebook.entry_point.getDbutils()
            .notebook()
            .getContext()
            .tags()
            .apply("user")
        )
        project_name = project_name.strip().replace(" ", "-")
        self.settings = {}

        if base_path is not None:
            base_path = base_path
        else:
            base_path = f"/home/{user}/health-lakehouse"

        if data_path is not None:
            data_path = data_path
        else:
            data_path = project_data_paths[project_name]

        dbutils.fs.mkdirs(base_path)
        delta_path = f"{base_path}/{project_name}/delta"

        experiment_name = f"/Users/{user}/{project_name}"
        if not mlflow.get_experiment_by_name(experiment_name):
            experiment_id = mlflow.create_experiment(experiment_name)
            experiment = mlflow.get_experiment(experiment_id)
        else:
            experiment = mlflow.get_experiment_by_name(experiment_name)

        self.settings["base_path"] = base_path
        self.settings["delta_path"] = delta_path
        self.data_path = data_path
        self.settings["data_path"] = data_path
        self.settings["experiment_name"] = experiment.name
        self.settings["experiment_id"] = experiment.experiment_id
        self.settings["artifact_location"] = experiment.artifact_location
        self.settings["tags"] = experiment.tags

    def load_remote_data(self, url, unpack=False):
        """
        Downloads a file from a remote URL and saves it to the specified data path.

        Args:
            url (str): The URL of the file to download.
            unpack (bool, optional): Whether to unpack the downloaded file. Defaults to False.
        """
        import requests

        fname = url.split("/")[-1]
        r = requests.get(url)
        print("*" * 100)
        print(f"downloading file {fname} to {self.data_path}")
        print("*" * 100)
        open(f"/dbfs{self.data_path}/{fname}", "wb").write(r.content)
        if unpack:
            print(f"unpacking file {fname} into {self.data_path}")
            import tarfile

            file = tarfile.open(f"/dbfs{self.data_path}/{fname}")
            file.extractall(f"/dbfs{self.data_path}")
            file.close()

    def print_info(self):
        """
        Prints the information stored in the settings dictionary.

        This method iterates over the settings dictionary and generates an HTML string
        to display the key-value pairs in a formatted way.

        Returns:
            None
        """
        _html = "<p>"
        for key, val in self.settings.items():
            _html += f"<b>{key}</b> = <i>{val}</i><br>"
        _html += "</p>"
        self.displayHTML(_html)

    def display_data(self):
        """
        Display the available data in the specified data path.

        If no data is available, it prints a message to run the `load_remote_data` method.
        Otherwise, it displays the list of files available in the data path.

        Args:
            None

        Returns:
            None
        """
        files = dbutils.fs.ls(f"{self.data_path}")
        if len(files) == 0:
            print("no data available, please run load_remote_data(<url for the data>)")
        else:
            print("*" * 100)
            print(f"data available in {self.data_path} are:")
            print("*" * 100)
            display(files)
