import csv
from itertools import pairwise
from datetime import datetime
from pprint import pprint
import yaml


def check_duplicate(iterable):
    return not len(set(iterable)) == len(iterable)


def find_min_date(line):
    my_date_min = datetime.today()
    found_date = False

    for key, value in line.items():
        if value and "Date" in key:
            try:
                my_date = datetime.strptime(value, "%m/%d/%Y")
                my_date_min = min(my_date_min, my_date)
                found_date = True
            except ValueError:
                continue
    if found_date:
        return my_date_min.date()
    else:
        print("No dates found")
        return False


def verify_personal(file):
    with open(file, "r") as f:
        reader = csv.DictReader(f)
        ids = [line["BSA Member ID"] for line in reader]
        f.seek(0)
        if not (
            all(
                (
                    line["First Name"],
                    line["Last Name"],
                    line["Unit Number"],
                    line["Parent 1 Email"],
                )
                for line in reader
            )
        ):
            print("some data missing")
            return False
        if check_duplicate(ids):
            print("duplicate id found")
            return False
    return True


def read_personal_scout(line):
    return {
        line["BSA Member ID"]: {
            "User ID": line["UserID"],
            "BSA ID": line["BSA Member ID"],
            "First Name": line["First Name"],
            "Suffix": line["Suffix"],
            "Last Name": line["Last Name"],
            "Nickname": line["Nickname"],
            "Address 1": line["Address 1"],
            "Address 2": line["Address 2"],
            "City": line["City"],
            "State": line["State"],
            "Zip": line["Zip"],
            "Home Phone": line["Home Phone"],
            "School Grade": line["School Grade"],
            "School Name": line["School Name"],
            "LDS": line["LDS"],
            "Swimming Classification": line["Swimming Classification"],
            "Swimming Classification Date": datetime.strptime(
                line["Swimming Classification Date"], "%m/%d/%Y"
            ).date()
            if line["Swimming Classification Date"]
            else None,
            "Unit Number": line["Unit Number"],
            "Unit Type": line["Unit Type"],
            "Date Joined Scouts BSA": datetime.strptime(
                line["Date Joined Scouts BSA"], "%Y-%m-%d"
            ).date()
            if line["Date Joined Scouts BSA"]
            else None,
            "Den Type": line["Den Type"],
            "Den Number": line["Den Number"],
            "Date Joined Den": datetime.strptime(
                line["Date Joined Den"], "%Y-%m-%d"
            ).date()
            if line["Date Joined Den"]
            else None,
            "Patrol Name": line["Patrol Name"],
            "Date Joined Patrol": datetime.strptime(
                line["Date Joined Patrol"], "%Y-%m-%d"
            ).date()
            if line["Date Joined Patrol"]
            else None,
            "Parent 1 Email": line["Parent 1 Email"],
            "Parent 2 Email": line["Parent 2 Email"],
            "Parent 3 Email": line["Parent 3 Email"],
            "OA Member Number": line["OA Member Number"],
            "OA Election Date": datetime.strptime(
                line["OA Election Date"], "%Y-%m-%d"
            ).date()
            if line["OA Election Date"]
            else None,
            "OA Ordeal Date": datetime.strptime(
                line["OA Ordeal Date"], "%Y-%m-%d"
            ).date()
            if line["OA Ordeal Date"]
            else None,
            "OA Brotherhood Date": datetime.strptime(
                line["OA Brotherhood Date"], "%Y-%m-%d"
            ).date()
            if line["OA Brotherhood Date"]
            else None,
            "OA Vigil Date": datetime.strptime(line["OA Vigil Date"], "%Y-%m-%d").date()
            if line["OA Vigil Date"]
            else None,
            "OA Active": line["OA Active"],
        }
    }


def read_personal(file):
    scouts = {}
    with open(file, "r") as f:
        reader = csv.DictReader(f)
        for line in reader:
            scouts.update(read_personal_scout(line))
    return scouts


def record_advancement_line(target, line):
    target["Date"] = find_min_date(line)
    target["Version"] = line["Version"]
    target["Date Completed"] = (
        datetime.strptime(line["Date Completed"], "%m/%d/%Y").date()
        if line["Date Completed"]
        else None
    )
    target["Approved"] = line["Approved"]
    target["Awarded"] = line["Awarded"]
    target["MarkedCompletedBy"] = line["MarkedCompletedBy"]
    target["MarkedCompletedDate"] = (
        datetime.strptime(line["MarkedCompletedDate"], "%m/%d/%Y").date()
        if line["MarkedCompletedDate"]
        else None
    )
    target["CounselorApprovedBy"] = line["CounselorApprovedBy"]
    target["CounselorApprovedDate"] = (
        datetime.strptime(line["CounselorApprovedDate"], "%m/%d/%Y").date()
        if line["CounselorApprovedDate"]
        else None
    )
    target["LeaderApprovedBy"] = line["LeaderApprovedBy"]

    # Scoutbook export for merit badges has the leaderapprovedby and leaderapproveddate columns reversed, so we reverse them
    try:
        target["LeaderApprovedDate"] = (
            datetime.strptime(line["LeaderApprovedDate"], "%m/%d/%Y").date()
            if line["LeaderApprovedDate"]
            else None
        )
    except ValueError:
        target["LeaderApprovedDate"] = (
            datetime.strptime(line["LeaderApprovedBy"], "%m/%d/%Y").date()
            if line["LeaderApprovedBy"]
            else None
        )
        target["LeaderApprovedBy"] = line["LeaderApprovedDate"]

    target["AwardedBy"] = line["AwardedBy"]
    target["AwardedDate"] = (
        datetime.strptime(line["AwardedDate"], "%m/%d/%Y").date()
        if line["AwardedDate"]
        else None
    )


def record_whole_award(scout, award_type, line):
    award_type = " ".join(award_type)
    if not f"{award_type}s" in scout:
        scout[f"{award_type}s"] = {}
    scout[f"{award_type}s"][line["Advancement"]] = {}
    record_advancement_line(scout[f"{award_type}s"][line["Advancement"]], line)


def record_rank_requirement(scout, award_type, line):
    if not "Rank Requirements" in scout:
        scout["Rank Requirements"] = {}
    rank = " ".join(
        [
            word
            for word in award_type[0:-2]
            if len(award_type[0:-2]) == 1
            or (len(award_type[0:-2]) > 1 and word != "Scout")
        ]
    )
    requirement = line["Advancement"].replace("#", "")
    if not rank in scout["Rank Requirements"]:
        scout["Rank Requirements"][rank] = {}
    scout["Rank Requirements"][rank][requirement] = {}
    record_advancement_line(scout["Rank Requirements"][rank][requirement], line)


def record_award_requirement(scout, award_type, line):
    award_type = " ".join(award_type)
    if not f"{award_type}s" in scout:
        scout[f"{award_type}s"] = {}
    if "#" in line["Advancement"]:
        award = " ".join(line["Advancement"].split()[0:-1])
        requirement = line["Advancement"].split()[-1].replace("#", "")
    else:
        award = line["Advancement"]
        requirement = line["Advancement"]
    if not award in scout[f"{award_type}s"]:
        scout[f"{award_type}s"][award] = {}
    scout[f"{award_type}s"][award][requirement] = {}
    record_advancement_line(scout[f"{award_type}s"][award][requirement], line)


def record_advancement(file, scouts):
    if scouts is None:
        scouts = {}
    with open(file, "r") as f:
        reader = csv.DictReader(f)
        for line in reader:
            if not line["BSA Member ID"] in scouts:
                print(
                    f"{line['Last Name']}, {line['First Name']} not found in personal data file"
                )
                scouts[line["BSA Member ID"]] = {
                    "BSA Member ID": line["BSA Member ID"],
                    "First Name": line["First Name"],
                    "Last Name": line["Last Name"],
                }
            scout = scouts[line["BSA Member ID"]]

            match line["Advancement Type"].strip().split():
                case ("Rank",) | ("Adventure",) | ("Award",) | (
                    "Merit",
                    "Badge",
                ) as award_type:
                    record_whole_award(scout, award_type, line)

                case (*r, "Rank", "Requirement") as award_type:
                    record_rank_requirement(scout, award_type, line)

                case (
                    ("Webelos" | "Wolf" | "Bear" | "Tiger" | "Lion"),
                    "Adventure",
                    "Requirement",
                ) | ("Adventure", "Requirement") | ("Award", "Requirement") | (
                    "Merit",
                    "Badge",
                    "Requirement",
                ) as award_type:
                    record_award_requirement(scout, award_type, line)

                case _:
                    pass

    return scouts


def create_scouts(personal_file, advancement_file):
    scouts = read_personal(personal_file)
    return record_advancement(advancement_file, scouts)


class Parser:
    def __init__(
        self,
        input_personal=None,
        input_advancement=None,
        outfile="output",
        file_format="yaml",
    ):
        if input_personal:
            self.scouts = record_advancement(
                file=input_advancement, scouts=read_personal(file=input_personal)
            )
        else:
            self.scouts = record_advancement(file=input_advancement, scouts=None)
        self.outfile = outfile
        self.file_format = file_format

    def dump(self):
        match self.file_format:
            case "yaml":
                import yaml

                with open(self.outfile, "w") as f:
                    yaml.safe_dump(self.scouts, f)
            case "toml":
                import toml

                with open(self.outfile, "w") as f:
                    toml.dump(self.scouts, f)
            case "json":
                import json

                with open(self.outfile, "w") as f:
                    json.dump(self.scouts, f)

    def dumps(self):
        match self.file_format:
            case "yaml":
                import yaml

                output_func = yaml.safe_dump
            case "toml":
                import toml

                output_func = toml.dumps
            case "json":
                import json

                output_func = json.dumps
        return output_func(self.scouts)


if __name__ == "__main__":
    parser = Parser(
        input_personal="Output_personal_data.csv",
        input_advancement="Output_advancement_data.csv",
        outfile="Output_scouts.yaml",
        file_format="yaml",
    )

    print(parser.dumps())
