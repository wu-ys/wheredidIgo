import os
import glob

if __name__ == "__main__":

    railway_gpx_files = sorted(glob.glob(os.path.join("./railway", "**", "*.gpx"), recursive=True))
    flights_gpx_files = sorted(glob.glob(os.path.join("./flights", "**", "*.gpx"), recursive=True))

    # load template and write
    with open("index_template.html", 'r', encoding='utf-8') as file:
        template = file.read()

    template = template.replace(f"{{railway}}", str(railway_gpx_files))
    template = template.replace(f"{{flights}}", str(flights_gpx_files))
    template = template.replace(f"\\\\", "/")

    with open("index.html", 'w', encoding='utf-8') as file:
        file.write(template)

    # load railway template and write
    with open("railway_template.html", 'r', encoding='utf-8') as file:
        template = file.read()

    template = template.replace(f"{{gpx_num}}", str(len(railway_gpx_files)))
    template = template.replace(f"\\\\", "/")
    with open("railway.html", 'w', encoding='utf-8') as file:
        file.write(template)

    # load flights template and write
    # load railway template and write
    with open("flights_template.html", 'r', encoding='utf-8') as file:
        template = file.read()

    template = template.replace(f"{{gpx_num}}", str(len(flights_gpx_files)))
    template = template.replace(f"\\\\", "/")
    with open("flights.html", 'w', encoding='utf-8') as file:
        file.write(template)    