# Example
```python
from sc_cc_ng_sdk_python import SCNGClient
from sc_cc_ng_models_python import ContextFilter, ContextRelation, SubContextFilter, ContextType

sdk_call = SCNGClient(url="http://localhost:8001/graphql")

tokens_list=[
    [
        "en-GB",
        "MY2022",
        "CT256",
        "EN06"
    ]
]

result = sdk_call(
    token_list=tokens_list,
    context_filter=ContextFilter(
        relation=ContextRelation.ALL,
        subContextFilters=[
            SubContextFilter(
                contexts=[
                    ContextType.MODEL,
                ],
                relation=ContextRelation.ALL
            )
        ]
    )
)
print(result.data)
print(result.error)
```