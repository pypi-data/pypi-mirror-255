# h2o-drive

H2O Drive Python Client.

## Installation

```sh
pip install h2o-drive
```

## Usage

### Connecting to H2O Drive

```py
import h2o_drive

drive = await h2o_drive.Drive()
```

When used within the [H2O AI Cloud](https://h2o.ai/platform/ai-cloud/) environment or locally with the [H2O AI Cloud CLI](https://docs.h2o.ai/h2o-ai-cloud/developerguide/cli) configured, no further configuration is needed.

`h2o_drive.Drive()` can be configured via its optional parameters:

- `token`: Token or token provider to use. If not specified, it's determined automatically.
- `endpoint_url`: URL of the Drive endpoint. If not specified, it's determined automatically.
- `sts_endpoint_url`: URL of the STS endpoint. If not specified, it's determined automatically.
- `environment`: URL of the H2O.ai cloud environment. Used only when determining a missing token or URL.
- `config_path`: Path to the H2O.ai CLI config. Used only when determining a missing token or URL.
- `session_ttl_seconds`: The duration, in seconds, of the role session.
- `read_timeout_seconds`: The time in seconds until a timeout exception is thrown when reading from Drive.

### Object Operations

To perform object operations, first navigate to the user's personal drive bucket:

```py
my_bucket = drive.my_bucket()
```

Continue operating at the root of the user's bucket (generally not needed) or navigate into a particular space (a.k.a. a directory path) with one of the following.  The `home` space is a good place to start.

```py
my_home_space = my_bucket.home()
# or
my_other_space = my_bucket.workspace("my_other_space")
```

Once in a space within a user's bucket (or the root of the bucket), the following operations are possible:

- `upload_file` uploads a local file to the user's Drive. It takes two arguments:
    - `file_name`: The file to upload.
    - `object_name`: The name to give to the uploaded file once it becomes an object in our Drive bucket.

- `list_objects` lists objects in the user's drive. It takes one optional argument:
    - `prefix`: When set, only objects whose names start with the specified prefix are returned.

- `download_file` downloads an object as a local file. It takes two arguments:
    - `object_name`: The name of the object (including prefix) to download.
    - `file_name`: Path to where the object should be saved as a local file.

- `delete_object` Deletes an object from the user's drive. It takes a single argument:
  - `object_name`: The name of the object (including prefix) to delete.

- `generate_presigned_url` generates a presigned URL through which an object in the drive can be accessed. It takes two arguments:
  - `object_name`: The name of the object (including prefix) to generate a presigned URL for.
  - `ttl_seconds`: (Optional) How long, in seconds, the URL should be good for.

## Examples

### Example: Connect to the `home` space of a user's drive bucket, write a local file, and then list the contents

```py
import h2o_drive

drive = await h2o_drive.Drive()

my_home_space = drive.my_bucket().home()

with open("test-file.txt", "w") as f:
    f.write("Hello, world!")

await my_home_space.upload_file("test-file.txt", "uploaded-object-name.txt")

objects = await my_home_space.list_objects()
print(objects)
```
