import csv

def filter_ri_dbr(infile, outfile, no_tags):
    with open(infile, "r") as dbrin, open(outfile, "w") as dbrout:
        reader = csv.DictReader(dbrin)
        header = reader.fieldnames
        if no_tags:
            header = [col for col in header if ":" not in col]
        print(header)
        writer = csv.DictWriter(dbrout, fieldnames=header, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        for row in reader:
            if row["ReservedInstance"] != "Y":
                continue
            out = {col:row[col] for col in header}
            writer.writerow(out)
