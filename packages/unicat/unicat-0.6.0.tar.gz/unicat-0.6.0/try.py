from pathlib import Path
from unicat import Unicat

connection = {
    "server": "http://cc.localhost",
    "project_gid": "84a1b5e4-fb5d-4ad6-a497-a3cf5eaf29b1",
    "api_key": "pynNf5w^pyF9PephC^d574N#pW3NN7qF",
}
CMS_GID = "99388f36-1707-4e22-97c3-874fdc8c1869"

folder = Path("files")
if not Path(folder).is_absolute():
    folder = Path(Path.cwd(), folder)
folder = folder.resolve()

unicat = Unicat(
    connection["server"],
    connection["project_gid"],
    connection["api_key"],
    folder,
)
if not unicat.connect():
    raise Exception("Invalid connection settings")

project = unicat.project
print(project.name)
# print(project.owner.username)
# print(project.default_language, project.languages)
# print(project.channels)
# print(project.orderings)
# print(project.fieldlists)
print()

channels = [project.channels["Website NL"]]

record = unicat.get_record(CMS_GID)
result = unicat.mutate.copy_record_channels_down(record, channels)
print(result)
print()

job = unicat.mutate.copy_record_channels_down(record, channels, return_job=True)
print(job, job.progress, job.return_value)
print()

job = unicat.mutate.copy_record_channels_down(record, channels, return_job=True)
for status in job.track():
    assert status == job.status
    print(job.name, job.status)
print(job, job.progress, job.return_value)
print()
