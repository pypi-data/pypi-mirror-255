# Getting Started

```python
from lqs import LogQS

lqs = LogQS()

log = lqs.resource.Log.fetch("My Log")
topic = log.list_topics(type_name="sensor_msgs/Image")[0]
record = topic.list_records()[0]
record.load_auxiliary_data_image()
```


## Setup

LogQS operates as a REST API service, meaning you can interact with it however you can make HTTPS requests.  However, it's much easier to use the LogQS Client Python library.  We will use the client for these docs, but be aware that these interactions don't require it.

First, we set up the environment by install [LogQS](https://pypi.org/project/LogQS):

```bash
pip install --upgrade LogQS
```

Then, we import the client class.


```python
from lqs import LogQS
```

To access a DataStore, the LogQS Client requires, at a minimum, three parameters to be explicitly configured:

- `api_key_id` - The ID of the API Key being used to access the service
- `api_key_secret` - The secret of the API Key being used to access the service
- `datastore_id` - The ID of the DataStore being accessed

An API Key can be generated from the Studio app. The API URL should be the "base" URL, e.g., `https://api.logqs.com`, and _not_ the URL of a specific endpoint, e.g., `https://api.logqs.com/apps/lqs/api`, etc.

These parameters can be passed to the client in a few ways:

- As parameters to the constructor (either as a `dict` or as a `RESTClientConfig` object)
- As environment variables (i.e., `LQS_API_KEY_ID`, `LQS_API_KEY_SECRET`, and `LQS_DATASTORE_ID`, which will be loaded from a `.env` file if present)
- As a configuration file (i.e., `logqs-config.json` with a single object containing the three parameters)

By default, the client will use the `api_url` of `https://api.logqs.com`.  If you are using a different API URL, you will need to pass it to the client.


```python
lqs = LogQS()
```

Generally, using LogQS involves either ingesting or querying record data. All record data is associated with a single topic, which is associated with a single log, which is associated with a single group.

In a fresh DataStore, you can ingest a log file by first creating a group then a log in that group. You can then upload a file to that log and create an ingestion for the file.  Once the ingestion process is complete, you can list the topics created by the ingestion and query records from those topics.

## Ingesting Data

Before you can ingest data, you must have created at least one group and at least one log. We can then upload files to that log (or, alternatively, use files from an external object sotre) and create ingestions for those files.

### Groups

A group is used simply for organizational purposes (all logs belong to one, and only one, group). A group requires a unique name. Group names can be changed later.

First, we will see if we have a group already created. We can do this by listing groups and filtering by a `name`. If no groups are returned, we will create one with the chosen name.


```python
# note that the resource is found on the 'data' attribute of the response object

group_name = "Demo Group"
groups = lqs.list.group(name=group_name).data
if not groups:
    group = lqs.create.group(name=group_name).data
else:
    group = groups[0]
group
```




    <Group id=4cc15840-bf96-4081-a387-14724c1b94a3, name=Demo Group>



If we know the ID of the group, we can fetch the group directly.


```python
# it's a bit redundant to query for a group just to use it's ID to fetch the group, but you get the idea
group = lqs.fetch.group(group_id=group.id).data

group
```




    <Group id=4cc15840-bf96-4081-a387-14724c1b94a3, name=Demo Group>



Many resources have a `note` field which can be used to store arbitrary refernce data. We can update the group's note to include a description of the group.


```python
group = lqs.update.group(
    group_id=group.id,
    data=dict(
        note="This is a note for the demo group."
    )
).data

group.note
```




    'This is a note for the demo group.'



#### Resource Models

Resource models can be accessed directly. These are [Pydantic](https://docs.pydantic.dev/) models, so you can use Pydantic methods, such as `model_dump()` to get a `dict` representation of the model, as well as additional LogQS methods.

For example, when a resource includes a "friendly ID" such as a group name, you can use the resource's `fetch` method to get the resource by that friendly ID:


```python
group = lqs.resource.Group.fetch("Demo Group")
group
```




    <Group id=4cc15840-bf96-4081-a387-14724c1b94a3, name=Demo Group>



You can also pass in an ID:


```python
group = lqs.resource.Group.fetch(group.id)
group
```




    <Group id=4cc15840-bf96-4081-a387-14724c1b94a3, name=Demo Group>




```python
# we can "detach" the resource from the client for convenience
Group = lqs.resource.Group

group = Group.fetch("Demo Group")
group
```




    <Group id=4cc15840-bf96-4081-a387-14724c1b94a3, name=Demo Group>



Using the resource model, we can fetch an existing group or create a new one with a single call:


```python
group = Group.fetch_or_create(name="Demo Group")
group
```




    <Group id=4cc15840-bf96-4081-a387-14724c1b94a3, name=Demo Group>



Instances of resource models can be updated. Calling the `update` method will update the resource in the service and update the local instance with the response:


```python
group.update(note="This is an updated note for the demo group.")
group.note
```




    'This is an updated note for the demo group.'



### Logs

Next, we can create a log. A log is a collection of topics (which, in turn, are collections of records). A log in LogQS can be composed of multiple log files (by ingesting multiple files), or it can be entirely virtual (by creating topics and records directly).

Informally, a log is a collection of records which are related. It's generally a good idea for logs to be partitioned by time (such as logs from a given run or a day), but this is not required. For example, a log could be a collection of records from a single day, or it could be a collection of records from a single hour, or it could be a collection of rolling records from an ongoing process etc. Similarly, a log could be partitioned by user, location, device, etc. For example, a fleet of machines could each have their own log which their data is pushed to, or a logical group of machines could push each of their data to a single log, etc.

Generally, it's a good idea for logs to be composed of records whose data is geospatially, temporally, and semantically close. However, LogQS is designed to be flexible and accommodate many different workflows, so it's encouraged to consider your use case and how you want to query your data when designing your logs.

How you organize logs will depend on the context of the records and how you want to query them, but note some of the limitations of logs which may affect your design:

- The number of ingestions, topics, records, etc. for a log is limited (configured on a DataStore level).
- The number of logs per DataStore is limited (configured on a DataStore level).
- Record data is partitioned by log, so records from different logs cannot be queried together.

When creating a log, we must specify the group it belongs to and a unique name for the log _within_ the group. Log names and group associations can be changed later. Logs have other optional parameters, such as a note, which can be set when creating the log.


```python
Log = lqs.resource.Log

# Note: a group ID and a log name are required to fetch a UNIQUE log or create a new one
Log.fetch_or_create(group_id=group.id, name="Demo Log")
```




    <Log id=27cce9af-2f88-4c45-8b72-dbf0054e7a80, name=Demo Log>




```python
lqs.list.log(group_id=group.id, name="Demo Log")
```




    LogListResponse(offset=0, limit=100, order='created_at', sort='asc', count=1, data=[<Log id=27cce9af-2f88-4c45-8b72-dbf0054e7a80, name=Demo Log>])



Some resources have sub-resources which can be accessed from the parent resource. For example, a log has topics, and a topic has records. These sub-resources can be accessed directly from the parent resource. For example, we can list the logs in a given group via the group's `list_logs` method:


```python
group = Group.fetch("Demo Group")
group.list_logs()
```




    [<Log id=27cce9af-2f88-4c45-8b72-dbf0054e7a80, name=Demo Log>]



### Objects

In LogQS, objects (files stored in an object store, like S3) are dedicated resources which can be used in a number of ways (namely, to ingest data from). Objects can be log files (such as ROS bags), but objects can also be configuration files, images, ML models, etc. LogQS provides endpoints for listing, fetching, and creating objects so that you don't need direct access to the object store.

Objects used in LogQS can be stored in either a LogQS-managed object store or a user-managed object store. LogQS-managed objects are always associated with one, and only one, log. When listing, fetching, and uploading log objects, you must specify the object's log. Processes cannot be associated with objects associated with logs other than the log it's associated with (e.g., an ingestion for one log cannot ingest data from an object associated with another log).

The client provides a utility function for uploading objects to LogQS. This function will automatically create the object and upload the file to the object store. The function requires the log ID the object will be associated with and the path to the file.


```python
(object, object_parts) = lqs.utils.upload_log_object(
    log_id=log.id,
    file_path="log.bag"
)
```

We can then fetch the object by key. This does _not_ fetch the object's content, but metadata about the object.


```python
object = lqs.fetch.log_object(log_id=log.id, object_key="log.bag").data
object
```




    <Object key=lqs/c28d67fc-9cfd-4dd0-9cde-e8ceea9975f5/logs/f94c2773-6075-44d3-9638-89489e99d0c0/log.bag>



If we want the object's content, we use the same function as above, but with the `redirect` parameter set to `True`. Optionally, we can also specify an offset and length to fetch a subset of the object's content.


```python
object_bytes = lqs.fetch.log_object(
    log_id=log.id,
    object_key="log.bag",
    redirect=True,
    offset=0,
    length=12
)
object_bytes
```




    b'#ROSBAG V2.0'



### Ingestions

An ingestion resource in LogQS is used to track the ingestion process of an object into a log. Ingestions must be associated with a log and an object. Ingestions have an optional `name` field, which can be used to identify the ingestion. Ingestion names are _not_ unique, so it's possible to have multiple ingestions with the same name.

By default, ingestions are created in a `ready` state, where they can be modified after creation. Once an ingestion is ready for processing, it's state can be changed to `queued`, which will trigger the ingestion process. Alternatively, ingestions can be created in a `queued` state, which will trigger the ingestion process immediately.


```python
Ingestion = lqs.resource.Ingestion

ingestion = Ingestion.fetch_or_create(
    log_id=log.id,
    name="Demo Ingestion",
    object_key="log.bag",
    state="queued"
)

ingestion
```




    <Ingestion id=8bde094d-0f90-43c4-b873-3ad76dc1ded5, name=Demo Ingestion>



#### Processing

By default, ingestions are created in a `ready` state. When an ingestion's state is transitioned to `queued`, the ingestion's processing workflow should be triggered, starting a job to run the process in the background. The process should transition the ingestion's state to `processing` while running, then it will transition to `finalized` when it is complete. Once all of the ingestion's part processes complete, the ingestion will transition to `completed`. If the ingestion fails, it will transition to `failed`.

During the `processing` state, the ingestion's `progress` field will be updated with the progress of the ingestion. If an error occurs during the ingestion, the ingestion's `error` field will be updated with the error message.

When we've queued an ingestion, we can re-fetch the ingestion to see its current state.


```python
ingestion = lqs.fetch.ingestion(ingestion.id).data
ingestion.state
```




    <ProcessState.queued: 'queued'>



The `refresh` method on resource models will re-fetch the resource from the service and update the local instance with the response.


```python
ingestion.refresh()

ingestion.state
```




    <ProcessState.queued: 'queued'>



### Topics

A topic is a collection of records for a given log. Topics include information about the records they contain, including the "type" of the record, i.e., information about how to parse the record data. During ingestion, topics will be created depending on the contents of the file ingested.


```python
log = Log.fetch("My Log")
topics = log.list_topics()
topics
```




    [<Topic id=950491af-4e7d-4c19-88eb-da03a12254c7, name=/crl_rzr/duro/piksi/pos_llh_cov>,
     <Topic id=ba40839f-ae71-4ad3-a45d-4cd100306f3e, name=/crl_rzr/duro/piksi/imu/data>,
     <Topic id=b1216184-3264-4eb2-9c41-740a627acd4b, name=/crl_rzr/vehicle/transmission/odometry>,
     <Topic id=0f552dad-30b5-4d93-b6a2-67403527fa3a, name=/crl_rzr/multisense_front/aux/image_color>]



We can filter the topics returned by `list_topics` based on attributes of the topic. For example, if we are only interested in image topics, then we can set the `type_name` filter to `"sensor_msgs/Image"`.


```python
topic = log.list_topics(type_name="sensor_msgs/Image")[0]
topic
```




    <Topic id=0f552dad-30b5-4d93-b6a2-67403527fa3a, name=/crl_rzr/multisense_front/aux/image_color>



### Records

A record is a single data point in a log. Records are characterized by the single topic they are associated with and a timestamp. A record's `timestamp` is an integer representing the number of nanoseconds since the Unix epoch, i.e., the same kind of timestamp returned by `time.time_ns()`.


```python
record = topic.list_records()[0]
record
```




    <Record timestamp=1655235727034130944, topic_id=0f552dad-30b5-4d93-b6a2-67403527fa3a, log_id=f94c2773-6075-44d3-9638-89489e99d0c0>


