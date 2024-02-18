import json
import pandas as pd
from dataclasses import dataclass
from lxml import etree
from entsopy.utils.const import *
from entsopy.utils.utils import *
from importlib import resources


@dataclass
class ResponseData:
    """
    Represents a response data object.

    Args:
        content (str): The content of the response.
        article_code (str): The article code.

    Attributes:
        root (etree.Element): The root element of the XML content.
        article_code (str): The article code.
        ns_name (str): The namespace name.
        nsmap (dict): The namespace map.
        data (list): The list of data rows.
        df (pd.DataFrame): The data in a pandas DataFrame.
        max_no_points (int): The maximum number of points.
        resolution (str): The resolution of the timeserie period.

    Methods:
        save_to_csv(file_name: str, path: str = ""): Saves the data to a CSV file.
        fill_missing_psr_types(all_psr_types: list = []): Fills missing PSR types in the data.
    """

    def __init__(self, content: str, article_code: str):
        content = content
        self.root = etree.XML(content)
        self.article_code = article_code
        self.ns_name = "ns"
        self.nsmap = get_namespace_from_root(self.root)

        data = []

        document_res = extract_elements_from_node(
            self.root,
            to_exclude=[
                "Point",
                "position",
                "quantity",
                "TimeSeries",
                "time_Period.timeInterval",
            ],
        )
        self.resolution = self.root.findtext(".//ns:resolution", namespaces=self.nsmap)
        self.date_start = datetime.strptime(
            document_res["doc.timeInterval.start"], "%Y-%m-%dT%H:%MZ"
        )
        self.date_end = datetime.strptime(
            document_res["doc.timeInterval.end"], "%Y-%m-%dT%H:%MZ"
        )
        timeseries = self.root.findall(
            f".//{self.ns_name}:TimeSeries", namespaces=self.nsmap
        )
        period = self.root.find(
            f".//{self.ns_name}:Period",
            namespaces=self.nsmap,
        )

        max_no_points = max_number_of_points(period, self.resolution, self.nsmap)

        for tms in timeseries:
            row = {}

            data_tms = extract_elements_from_node(
                tms, to_exclude=["Point", "position", "quantity"], prefix="tms"
            )

            for i in range(1, max_no_points + 1):
                data_point = {}

                data_timing = get_time_data(
                    date_start=self.date_start,
                    date_end=self.date_start,
                    resolution=self.resolution,
                    position=i,
                )

                data_point["position"] = i
                data_point["quantity"] = get_point_quantity(tms, i, self.nsmap)
                row = {
                    **document_res,
                    **data_tms,
                    **data_timing,
                    **data_point,
                }
                data.append(row)

        self.data = data
        self.df = pd.DataFrame(self.data)
        self.max_no_points = max_no_points

        if self.article_code == "14.1.A" or self.article_code == "16.1.B&C":
            self.fill_missing_psr_types()
        elif self.article_code == "14.1.D":
            self.fill_missing_psr_types(all_psr_types=["B16", "B18", "B19"])

    def save_to_csv(self, file_name: str, path: str = ""):
        timestamp = (datetime.now()).strftime("%Y%m%dT%H%M%S")
        self.df.to_csv(
            f"{file_name}-{self.article_code}-{timestamp}.csv",
            index=True,
            index_label="id",
        )

    def fill_missing_psr_types(
        self,
        all_psr_types: list = json.load(resources.open_text("entsopy.data.types", "psrtypes.json"))
    ):    
                
        psr_type = self.df["mkt.psrType"].unique()

        missing_psr_types = [psr for psr in all_psr_types if psr not in psr_type]

        for i in range(1, self.max_no_points + 1):
            for missing_psr_type in missing_psr_types:
                new_row = self.df[:1]
                new_row["quantity"] = "na"
                new_row["position"] = i
                new_row["mkt.psrType"] = missing_psr_type
                self.df = pd.concat([self.df, new_row])

                data_time = get_time_data(
                    self.date_start,
                    self.date_start,
                    position=i,
                    resolution=self.resolution,
                )

                for key, value in data_time.items():
                    new_row[key] = value

        if self.article_code == "14.1.A" or self.article_code == "16.1.B&C":
            self.df = self.df.sort_values(by=["mkt.psrType"])

        self.df = self.df.reset_index(drop=True)
