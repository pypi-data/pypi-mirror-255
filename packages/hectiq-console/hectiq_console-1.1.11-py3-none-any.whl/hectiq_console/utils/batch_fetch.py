from typing import Callable, Optional, Any, List
try:
    from rich.progress import Progress
except:
    Progress = None

class BatchFetch():
    """A helper class to use the paginate API of the Hectiq Console.
    
    It can be used as an iterator or its `get_all` method can be called to get all the results.

    For example:

    ```python
    fetcher = BatchFetch(method=api.get_jobs, batch=10, limit=1000)
    results = fetcher.get_all()
    ```

    or 

    ```python
    fetcher = BatchFetch(method=api.get_jobs, batch=10, limit=1000)
    for results in fetcher:
        print(results)
    ```
    """
    def __init__(self, method: Callable, batch: int = 100, limit: Optional[int] = None, **kwargs):
        """Initialize the BatchFetch object.

        Args:
            method (Callable): The method to call to fetch the data.
            batch (int, optional): The batch size. Defaults to 100.
            limit (Optional[int], optional): The limit of the number of results to fetch. Defaults to None.
            **kwargs: The keyword arguments to pass to the method.
        """

        self.kwargs = kwargs
        self.limit = limit
        self.batch = batch
        self.page = 1
        self.method = method
        self.total_pages = None

    def get_all(self) -> List[Any]:
        """Get all the results. It iterates over the batches and returns the list of results.

        Returns:
            list: The list of results.
        """
        def iterate(progress=None, task=None):
            results = []
            for results_batch in self:
                results += results_batch
                if progress is not None and task is not None:
                    progress.update(task, advance=1, total=self.total_pages)
                if self.limit and len(results) >= self.limit:
                    break
            return results
        if Progress:
            with Progress() as progress:
                task = progress.add_task("[blue]Fetching...")
                return iterate(progress, task)
        else:
            return iterate()

    def get(self) -> List[Any]:
        """Get the next batch of results.
        """
        results = self.method(page=self.page, limit=self.batch, **self.kwargs)
        self.total_pages = results.get("total_pages")
        if results.get("total_pages") < self.page:
            raise StopIteration
        if self.limit and self.page * self.batch > self.limit:
            raise StopIteration
        self.page += 1
        return results["results"]
    
    def __iter__(self):
        return self

    def __next__(self):
        return self.get()
    
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.page = 1
        pass