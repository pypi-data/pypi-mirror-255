# smcore

smcore provides base class agents and blackboard clients for use with [SimpleMind's go implementation](https://gitlab.com/hoffman-lab/core).

**This is still a work in progress and not yet ready for "primetime." Functionality and API are likely to change until this message is removed and we start taking version numbers seriously.**

## Getting started

1. Install `smcore` from PyPi (this is currently the _only_ supported means to install and use this library)

```
pip install smcore
```

2. Generate an empty Python agent using `core`. Note: you will need to have the `core` tool installed on your system. Please see the root README (or ask John) for more instructions.

```
./core generate python-agent --name hello-agent
```

You should use "kebab" case (all lowercase, words separated with dashes) when naming agents. For instance, the following **are** valid agent names:

- `my-new-agent`
- `kidney-segmentation-agent`
- `grab-daily-news-worker`
- `my-new-agent-2`

The following are **NOT** valid agent names:

- `My New Agent`
- `KidneySegmentationAgent`
- `grabDailyNewsWorker`
- `2-my-new-agent`

Although this may not be perfectly enforced at this point (eventually we'll validate it for the user), this is the naming scheme we intend to support. This is a very deliberate choice as certain cloud infrastructure expects names to be in this format. Note that numbers are fine, just don't start an agent name with a number (example above).

3. Start a local SM blackboard in server mode

```
./core server
```

4. Launch your agent!

```
python hello_agent.py --blackboard localhost:8080 --spec '{"name":"HelloAgent"}'
```

You should see two messages appear on the blackboard: a "Hello" message and a "Goodbye" message.

**Congrats! You've just run your for SM agent.**

5. Extra credit: Customize the commented-out Log message to see one mechanism with which agents can communicate with the blackboard.

## The Agent API

Under `core` an Agent is anything that communicates with the blackboard. As you can see from the generated example above, we provide a base class that handles all of networking and communication and exposes a minimal, (hopefully) easy-to-use set of functions to send different message types. We'll work on better documentation over time, but this is the essentials.

In the below sections, "self" always refers to the agent object/class.

### Overview

There are essentially only five API calls you need to be familiar with and one "concept" that works with these API calls:

API:

1. Log to the blackboard from your agent (`self.log(...)`)
1. Post an agent status update (`self.post_status_update(...)`)
1. Post a result, partial result, or no results (`self.post_result(...)`, `self.post_partial_result()`, etc.)
1. Read attributes (`self.attribute(...)`)
1. Await data (`await self.await_data()`)

Concept:

1. A "promise" for data resolution (`"attribute_name": "Promise(ResultName as ResultType from AgentName)" `)

All of these are explained in detail below. Any feedback on improvements to this section (including typos since we're in the early stages) can be put in issues or a merge request. If filing typo/wording-related merge requests, please group as many edits as possible into a single MR to make them easier for us to review.

### Log Messages

Think of this as your "stdout" to the blackboard. Useful to track updates for human readers. Generally, agents should not/will not parse log messages.

```
self.log(severity, message)

  'severity' is an enumerated type, one of:

    Log.DEBUG		- Messages that should generally be suppressed once the agent is running correctly
    Log.INFO		- Messages that should appear on the blackboard; generally for human readers
    Log.WARNING		- Agent has encountered an unexpected state, but can continue processing unimpeded
    Log.ERROR		- Agent has encountered an unexpected state where it cannot continue processing normally, however, may be able to continue running (i.e. recover, wait for new data, etc.)
    Log.CRITICAL	- Something has gone wrong and the agent is shutting down because of the situation

  'message' is a string you'd like to appear on the blackboard
```

to use the enumerated Log types (recommended), you will need to import Log from smcore:

```
from smcore import Agent, Log
```

Some examples of logging:

```
MyAgent.log(Log.INFO,"Just checking in")
MyAgent.log(Log.ERROR,"DB connection dropped. Retrying...")
MyAgent.log(Log.CRITICAL,"Computer out of memory")
```

### Status Updates

Status updates indicate a change in the state of an agent.

Generally used for dependency resolution and by the controller for monitoring.

For server-style agent/blackboard interaction, these messages are not required, however using them will enable better support for monitoring via connected dashboards, metrics gathering, etc.

```
self.post_status_update(state, message):

  'state' is an enumerated type, one of:

    AgentState.UNKNOWN			- Essentially the "null" state
    AgentState.OK				- Agent has said hello
    AgentState.REQUESTED		- Agent requested, but has not said hello
    AgentState.AWAITING_PROMISE - Agent is awaiting promised results
    AgentState.WORKING			- All promises fulfilled, currently processing
    AgentState.MISSING			- No pings detected (set by the controller/monitor)
    AgentState.ERROR			- Agent has encountered an error and cannot proceed normally
    AgentState.COMPLETED		- All agent tasks completed (should precede the agent goodbye/shutdown)

  'message' is a string with information about the current state
```

to use the enumerated AgentState types (recommended), you will need to import AgentState from smcore:

```
from smcore import Agent, AgentState
```

Some examples of status updates:

```
MyAgent.post_status_update(AgentState.OK,"")
MyAgent.post_status_update(AgentState.AWAITING_PROMISE,"listening for lung segmentations...")
MyAgent.post_status_update(AgentState.AWAITING_PROMISE,"listening for nodule ROIs...")
MyAgent.post_status_update(AgentState.ERROR,"Expected an array of 512x512, but got 0x0")
MyAgent.post_status_update(AgentState.ERROR, traceback.format_exc())
```

### Posting Results

"Results" are your _key_ mechanism for passing data between agents. It is intended to be extremely permissive in that you can (and should!) just stuff data into it as if it were an envelope, and post it to the BB. All of the data management and sharing is handled\* for you.

(\* There are some caveats to this statement in the early stages of this, but that's the direction that we're headed and want to get to. Currently, it's handled, but not in a truly scalable way.)

```
MyAgent.post_result(res_name: str, res_type: str, data: dict):

  'res_name' is a string identifying the result. Required and should (must?) be non-empty.

  'res_type' is a string identifying the result type. Required and should (must?) be non-empty.

  'data' is a json-friendly dictionary containing any data that comprises the result.

'res_name' and 'res_type' are user/agent configurable and left entirely up to the user.  Complexity/simplicity of naming schemes will likely be problem specific so we can't offer much guidance other than it could be worth giving this some thought before you start coding.

We will eventually add (fix) wildcard '*' support so that promises can be resolved for any result, type, or agent.

'data' currently seems to work pretty well, however, JSON serialization can sometimes be a bit unpredictable.  Most of our experience is from Go, so Python might do things we're not aware of. If you run into issues where serialization does not work correctly or does something unexpected, please file an issue in the core repository.
```

It's important to not limit yourself to just passing one output either.

The data argument is a Python dictionary in the truest sense that you can stuff multiple (potentially unrelated?) chunks of data into it and save them to the blackboard. Use this to pass data to make downstream processing of the results easier.

A somewhat trivial example might be attaching the input parameters used to generate the result:

```
data = {
    "erosion_element": "disk",
    "erosion_radius": 3,
    "input_data": "Promise(LeftLungMask as LungSegmentation from LeftLungSegmentationAgent)",
    "message": "unexpected or anomalous region detected (topology, too many holes). maybe emphysema or DLD? Could produce unexpected erosion results.",
	"eroded_mask": np.array(...),
}
```

Play with it and favor slightly more data than less!\*

(\*Again, in the early stages, we may get bitten passing excessive amounts of data, but in the long run, we should be favoring passing additional/extra data that downstream agents can utilize in ways we may not expect or plan for in our agents.)

Some examples of posting results:

```
MyAgent.post_result(
    "LeftLung",
    "LungSegmentation",
    data = {
        "algorithm_version": "1.0.1",
        "mask": np.Array(...)
})

MyAgent.post_result(
    "NoduleDetectionSummary",
	"FinalMetric",
	data = {
        "input_cases": ["case1", "case2"],
        "sensitivity": 0.4,
        "specificity": 1.0,
        "AUC": 0.75,
        "N": 2,
        "message": "N is very low and these figures may not be accurate to the group from which data was sampled."
	}
)
```

#### Partial results and no results

"Partial result" and "no result" have the same signature as a regular result, however, they indicate different things to downstream agents about the data provided.

```
MyAgent.post_partial_result(res_name, res_type, data)
```

"Partial result" indicates that "I've finished processing my input and produced results, but either there is additional processing I will continue doing, or I will wait for a new input." You could also utilize a partial result as a multi-part solution, or incrementally improved results over time.

```
MyAgent.post_no_result(res_name: str, res_type: str, data: dict)
```

"No result" indicates that the agent was not able to find a result for a given input, despite _everything functioning correctly_. Please do **not** use "no results" for error messages, although if you wish to indicate reasons why a result was not able to be found, that is appropriate.

#### Passing data with no results

Perhaps somewhat paradoxically, you can attach data to the "no results" message type. This is by design and can be used to pass problem context even in the event of the agent failing to find a solution.

- **Example 1**: A lung segmentation agent was trained on a specific input domain of images from Siemens scanners, and should not be applied to any GE data. The agent could parse the header for manufacturer information and reject cases from GE scanners. The way that it would communicate this to any downstream agents waiting for lung segmentations would be to post a "no result" and perhaps the data `{"message":"not trained to segment from GE scanners"}`.

- **Example 2**: A more interesting example would be passing meaningful data. Again, let's say that our lung segmentation agent knows that it produces an accurate segmentation if the noise in the trachea/aorta is below a certain threshold. The current case is well above the needed threshold, however, maybe we want to still provide an attempt that we will analyze later, just one that definitely cannot be trusted if a downstream agent depends on a good lung segmentation. Here you would post the attempted lung segmentation as the _data_ on the "no results" message.

- **Example 3**: You could also use no result data to pass hints and data as to what went wrong. Perhaps our input data for our lung segmentation agent passes all of our sanity checks, however, when it goes to process the case it notices that there is a topological inconsistency to the segmentation data (for instance, an unexpected hole, or a missing lung.

See the `post_result` example above for examples of using `post_partial_result` and `no_result` (you'll just need to change the function name, however, the calling pattern is the same).

### Accessing attributes

```
MyAgent.attribute(name)
```

"Attributes" are the mechanism to pass data to your agent either through the knowledge base (config file) or via the command line. It may feel a little cumbersome, or at least unnecessary, at first, but due to the distributed nature of this communication backbone, you must develop your agents using attributes rather than writing custom command line parsing. If you're interested in the details of why this is, let us know via an issue and we'll add a section to this document explaining it in more detail.

Attributes are passed via the agent specification or "spec".

For example, to start the python ping agent included in the [core](https://gitlab.com/hoffman-lab/core) repository (found at `python/ping_agent.py`), the minimum acceptable command line call would be:

```
python ping_agent.py --blackboard localhost:8080 --spec '{"attributes":{"dwell":3}}'
```

As you can see, we've passed one attribute called "dwell" with a value of 3 to our agent.

To access this attribute inside of our agent, we just use the `attribute` method provided by the agent API:

```
dwell_time = ping_agent.attributes("dwell")
jitter_sec = 0.3
time.sleep(dwell_time + jitter)
```

#### A word of caution

Because this system is SO permissive and Python generally lacks strong typing, we can't (won't) offer strong guarantees that attributes will be typed correctly. _It is up to the agent developers_ to ensure that data is being written and read as expected between agents.

As you find cases where there are failures or unexpected behaviors, please file [issues](https://gitlab.com/hoffman-lab/core/-/issues) to help us understand where the current system is not working and can be improved.

### Awaiting data

Having your agent sit idle until it receives required input data (via promises) is likely to be a common action among many/most agents, so we've provided a convenience method for it:

```
self.await_data()
```

Due to the asynchronous nature of our computing model, you have to call it using Python's `await` keyword:

```
await self.await_data()
```

Once the agent moves on from this hold, all of the desired/promised data can be retrieved using the attributes system described above! This is just one of the reasons why it is important to only use the attributes system to pass data between the user, blackboard, and agents.

(NOTE: This promise system may not be fully implemented in Python just yet, but this description is the intended functionality. As soon as you run into issues with this, tell John so we can prioritize getting it working correctly. Also, it's safe to expect that it's not working correctly if it's not working as described. You're probably not misunderstanding anything!:))

### Receiving data from other agents

We've covered how your agents can add data to the blackboard, but how do your agents discover, read, and process data from the blackboard data from the blackboard?

In core, this is done through a system based on the concept of "promises". Although this is a common term in computer science (we borrowed it from Javascript), don't take it too literally if you go looking for documentation. Ours is much less rigid than some of the strict specifications but does share a lot of conceptual ideas under the hood. The good news though is that you shouldn't have to worry too much about how things are implemented and can focus on just using the promise system to trigger your agent when new data is available.

Promises in core look like this:

```
attribute_name: Promise(ResultName as ResultType from AgentName)
```

Promises are declared via attributes in your agent spec (which is passed when the agent is started). For instance:

In the context of a full agent spec, let's say we've saved the following in a JSON file (`spec.json`):

```
{
	"name": "TestAgent",
	"pingIntervalMs": 1000,
	"pollIntervalMs": 1000,
	"attributes": {
		"incoming": "Promise(LungCT as DicomData from DicomInputAgent)"
	}
}
```

Here, we've expressed that this agent is expecting promised "LungCT" data of type "DicomData" (as opposed to say "NiftiData" which it may not be able to parse) from a specific agent, "DicomInputAgent". With this declaration, TestAgent is now a _downstream_ agent of DicomInputAgent.

To launch this agent via the command line, we would run:

```
python3 test_agent.py --blackboard localhost:8080 --spec `cat spec.json`
```

#### Wildcards in promises (under development!!!)

**As of the start of this upcoming sprint, wildcards are not currently working although the basics are in place to support them. We will prioritize fixing this as soon as there is demand!**.

Any of the fields in a promise can be replaced with a wildcard (\*, similar to the linux/mac command line), which means that the promise can be fullfilled by multiple other agents, multiple types of data, or multiple data sets. (You could theoretically trigger on any result posted to the blackboard by using all wildcard characters, although we don't recommend that you do this...)

**Example 1:** Say we wanted to trigger a DICOM anonymization agent that scans _all DICOM results_ (from any agent providing `DicomData` result types) for PHI and private fields. We could trigger this agent with the following promise:

```
Promise( * as DicomData from * )
```

**Example 2:** Say we had multiple lung segmentation agents, each running a different algorithm and we had an analysis tool that would fuse each lung result with the original DICOM data to analyze the segmentation quality. The promises we might use to trigger this agent would be (in JSON format):

```
"lung_seg": "Promise(Lung as Segmentation from *)"
"lung_dicom": "Promise(LungStudy as DicomData from DicomInput)"
```

#### Final thoughts on promises

Think of a promise like a reverse "IOU": instead of someone promising to deliver you something, you (i.e. your agent) draft the IOU yourself and declare what you expect to receive and from whom. There's no guarantee you'll receive it, but it expresses a contract between you and the blackboard that this is the sort of data your agent is interested in.

**How you name your promises and results (including types) is key to a healthy, workable pipeline,** and will almost always be problem-specific. Don't be afraid to discuss in advance, revise, etc. about what naming schemes will work for your agents. Also, don't be afraid to occasionally over-trigger your agents. Theoretically, it'll just generate a few additional results which we may find turn out to be useful.

### That's it!

To recap, there's only really five things you need to worry about with our Agent API:

- Logging: `agent.log(severity, message)`
- Status updates: `agent.post_status_update(state, message)`
- Results/partial results/no results:
  - `agent.post_result(res_name, res_type, data)`
  - `agent.post_partial_result(res_name, res_type, data)`
  - `agent.post_no_result(res_name, res_type, data)`
- Attributes:
  - `attribute_value = agent.attribute(attribute_name)`
- Awaiting data: `await self.await_data()`

There's not much in the way of a "promises" API (it's baked into the above agent methods), but it is important to at least understand the concept.

Hopefully, this feels pretty barebones. If so, that's very intentional! If not, we want to hear how you would change things in our [issues](https://gitlab.com/hoffman-lab/core/-/issues).

## A little bit about the "core" philosophy

This is a big shift from the previous simple mind implementation and conceptually we want to make a few things clear.

1. `core` is intended to be a scalable, high-throughput communication layer for blackboard-based, cognitive computing. It does not inherently do any computing of its own, beyond some basic agents that manage other agents (the controller and runners).

1. No domain-specific code (i.e. medical imaging, neural networks, etc.) should ever make it into `core` or its Python API. All of that should be left to agent design and development. We will close merge requests that include (even accidentally) any domain-specific code.

1. `core` and its APIs should be thought of essentially as a separate, 3rd party project/library from the rest of SimpleMind.

That final point is very important. We don't want to be obtuse or difficult, but rather it is to ensure that we all have a highly stable base to build from, and shared language used to communicate between agents. That, by design, should only seldomly change, and when it is changed, it should not be without extensive discussion, forethought, intention, and backward-compatibility prioritization.

It also adds an interesting "pressure" the to overall SM project where the core devs (John and Josh) will work to optimize the communication layer, while other teams and projects work to optimize the learning and knowledge layers. I suspect those competing yet mutually beneficial goals will also allow for a cleaner, better, more performant implementation of each in the long run, however, that may mean you don't always get exactly what you want as fast as you want it (or at all).

We want to be responsive to the needs of the users though, but just know that requesting or proposing changes to the core should be a last-ditch option. You should always try to solve your problems in the agent layer _first_, and you may need to get creative.

**Early CVIB users:** While all of the above is true and holds, we're still in the early days of this and we recognize that there will be bugs or choices that we've made early on that need to be revised. As we're all getting up and running, please don't let the above statements discourage you from asking us questions or proposing alternatives to the initial implementations. It's probably going to take a few versions before we get this nailed down!
