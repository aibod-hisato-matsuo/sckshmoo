import reflex as rx
import os
import shutil

from shmooapp.config import PLOTSDIR, ARCHIVEDIR
from shmooapp.analysis.common_utils import extract_logfilename_from_path,generate_arcdir,collect_archived_logs, generate_aggfile_name
from shmooapp.analysis.create_shmooplot_files import extract_test_results
from shmooapp.analysis.fill_missing_vdd import update_files_for_vdd
from shmooapp.analysis.update_shmoo_range import update_files_for_range
from shmooapp.analysis.calculate_margin import calculate_files_for_margin
from shmooapp.analysis.aggregated_shmoo import process_aggregation
from shmooapp.analysis.xor_shmoo import process_xor


class FileState(rx.State):
    """The app state."""

    # Property to store the paths of selected folders
    file_paths: list[str] = []   # ex) [""./D5700xxx.log",]
    pathstr : str = ""           # ex) uploaded_dir/D5700xxx

    # process01
    logbasedir : str = ""           # ex)  out.range/D5700xxx
    subdirs : list[str] = []
    curdir : str = ""
    subfiles: list[str] = []
    subfile_texts : list[str] = []
    margin_sets : list[list[float,float,float,float]] = []
    aggregation_sets : list[str] = []

    # process02
    aggregation_file_or : str = ""
    aggregation_file_and : str = ""
    aggregation_file_mj : str = ""
    aggfile_texts : list[str] = []
    xordir : str = ""
    xorfiles: list[str] = []
    xorfile_texts : list[str] = []

    # log hisotry
    archive_dir : str = ARCHIVEDIR
    archived_logs : list[str] = []

    #def __init__(self):
    #    self.pathstr: str = ""

    @rx.event
    async def handle_upload(self, files: list[rx.UploadFile]):
        # Extract and store the paths of the uploaded folders
        for file in files:
            upload_data = await file.read()
            outfile = rx.get_upload_dir() / file.filename
            self.pathstr = str(outfile)
            print(f"{outfile}")

            # Save the file.
            with outfile.open("w",encoding="utf-8") as file_object:
                decoded_data = upload_data.decode("utf-8")
                file_object.write(decoded_data)
        
            self.file_paths.append(outfile)

    @rx.Var
    def convert_to_str(self)->str:
        return self.pathstr

    def put_pathstr(self):
        for file in self.file_paths:
            outfile = rx.get_upload_dir() / file.filename
        return outfile

    def clear_vars(self):
        self.file_paths = []
        self.curdir = ""
        self.subdirs = []
        self.subfiles = []
        self.subfile_texts = []
        self.margin_sets = []
        self.aggregation_file_or = ""
        self.aggregation_file_and = ""
        self.aggregation_file_mj = ""
        self.aggfile_texts = []
        self.xordir = ""
        self.xorfiles = []
        self.xorfile_texts = []

    # process 01
    def run_process01_1(self):
        filepath = self.pathstr
        outpath = PLOTSDIR
        self.subdirs = extract_test_results(filepath,outpath)

    def p01_read_plots(self, directory: str):
        self.margin_sets = []
        self.curdir = directory
        self.subfiles = sorted(os.listdir(directory))
        self.subfile_texts = []
        for file in self.subfiles:
            filepath = os.path.join(directory,file)
            with open(filepath,encoding='UTF-8') as f:
                text = f.read()
            self.subfile_texts.append(text)

    def run_process01_2(self):
        print(f"Proc01-2: {self.curdir}")
        update_files_for_vdd(self.curdir)

    def run_process01_3(self):
        print(f"Proc01-3 : {self.curdir}")
        update_files_for_range(self.curdir)

    def run_process01_4(self):
        print(f"Proc01-4 : {self.curdir}")
        self.margin_sets = calculate_files_for_margin(self.curdir)

    def run_process01_calc(self):
        self.run_process01_2()
        self.run_process01_3()
        self.p01_read_plots(self.curdir)
        self.run_process01_4()

    # process 02
    def run_process02_1(self):
        print(f"Process02-1 : {self.curdir}")
        self.aggregation_file_or = process_aggregation(self.curdir,"OR")
        self.aggregation_file_and = process_aggregation(self.curdir,"AND")
        self.aggregation_file_mj = process_aggregation(self.curdir,"Majority")
        self.aggregation_sets = []
        self.aggregation_sets.append("OR")
        self.aggregation_sets.append("AND")
        self.aggregation_sets.append("MajorityVote")

    def run_process02_2(self,mode:str):
        print(f"Process02-2 : {self.curdir} with {mode}")
        file = self.select_aggregation_file(mode)
        prefix = f"{mode}_XOR" # AND, OR, MajorityVote
        self.xordir = process_xor(self.curdir,file,prefix)

    def select_aggregation_file(self,mode:str):
        if mode == "AND":
            return self.aggregation_file_and
        elif mode == "OR":
            return self.aggregation_file_or
        else: # Majority Vote
            return self.aggregation_file_mj

    def p02_read_plots(self):
        self.aggfile_texts = []
        for filepath in [self.aggregation_file_or,self.aggregation_file_and,self.aggregation_file_mj]:
            with open(filepath,encoding='UTF-8') as f:
                text = f.read()
            self.aggfile_texts.append(text)

    def p02_read_plots_xor(self):
        self.xorfile_texts = []
        self.xorfiles = sorted(os.listdir(self.xordir))
        for file in self.subfiles:
            filepath = os.path.join(self.xordir,file)
            with open(filepath,encoding='UTF-8') as f:
                text = f.read()
            self.xorfile_texts.append(text)

    def run_process02_1_calc(self):
        self.run_process02_1()
        self.p02_read_plots()
    
    def run_process02_2_calc(self,mode:str):
        self.run_process02_2(mode)
        self.p02_read_plots_xor()

    # automation
    def run_each_test(self,directory:str):
        self.p01_read_plots(directory)
        self.run_process01_calc()
        self.run_process02_1_calc()
        for agg in self.aggregation_sets:
            self.run_process02_2_calc(agg)

    def run_all_tests(self):
        self.run_process01_1()
        for test in self.subdirs:
            self.p01_read_plots(test)
            self.run_process01_calc()
            self.run_process02_1_calc()
            for agg in self.aggregation_sets:
                self.run_process02_2_calc(agg)
    
    # archive log plots dir
    def run_archive(self):
        filepath = self.pathstr
        filename = extract_logfilename_from_path(filepath)
        plotsdir = os.path.join(PLOTSDIR, filename)
        arcdir = generate_arcdir(ARCHIVEDIR,filename)
        self.archive_dir = arcdir
        print(f" {filepath} : {filename} -> {plotsdir}, copy to {arcdir}")

        # Ensure the source directory exists
        if not os.path.exists(plotsdir):
            raise FileNotFoundError(f"Source directory '{plotsdir}' does not exist.")
        
        # Copy logbasedir to arcdir
        try:
            shutil.copytree(plotsdir, arcdir, dirs_exist_ok=True)
            print(f"Successfully copied '{plotsdir}' to '{arcdir}'.")
        except Exception as e:
            print(f"Error copying directory: {e}")

    def get_archived_log(self):
        self.archived_logs = []
        self.archived_logs = collect_archived_logs(ARCHIVEDIR)
        for dir in self.archived_logs:
            print(f"{dir}")

    def set_archived_log_for_view(self,directory):
        self.pathstr = directory
        self.subdirs = collect_archived_logs(directory)
    
    def set_plots_vars(self,directory:str):
        self.curdir = directory
        self.margin_sets = calculate_files_for_margin(self.curdir)
        self.aggregation_file_or = generate_aggfile_name(self.curdir,"OR")
        self.aggregation_file_and = generate_aggfile_name(self.curdir,"AND")
        self.aggregation_file_mj = generate_aggfile_name(self.curdir,"Majority")
        self.p01_read_plots(directory)
        self.p02_read_plots()