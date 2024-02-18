
from dataclasses import dataclass, field
from requests import post
from sc_cc_ng_models_python import ContextFilter, BitVal
from typing import List, Optional, Any
from itertools import starmap

@dataclass
class KeyValue:
    
    """
        A key value pair.
    """

    key: str
    value: Any

    def __hash__(self) -> int:
        return hash(self.key + str(self.value))
    
    def to_dict(self) -> dict:
        return {
            "key": self.key,
            "value": self.value,
        }

@dataclass
class BitCollection:

    """
        A collection of bit values.
    """

    tokens: List[str] = field(default_factory=list)
    bits: List[BitVal] = field(default_factory=list)

    def as_key_values(self) -> List[dict]:
        return list(
            map(
                lambda bit: KeyValue(
                    key=" ".join(bit.context),
                    value=bit.value,
                ),
                self.bits
            )
        )

@dataclass
class BitCollectionComposer:

    """
        A class for composing bit collections.
    """

    collections: List[BitCollection] = field(default_factory=list)

@dataclass
class Result:

    """
        A result object, containing data if everything was ok else an error.
    """

    data:   Optional[Any]   = None
    error:  Optional[str]   = None

@dataclass
class SCNGClient:

    url: str

    def __call__(self, token_list: List[List[str]], context_filter: ContextFilter) -> BitCollectionComposer:
        
        try:
            response = post(
                self.url, 
                json={
                    "query": """
                        query TokenListQuery($tokenList: [[String!]!]!, $contextFilter: ContextFilter!) {
                            tokenListBasedContent(tokenList: $tokenList) {
                                meta(
                                    contextFilter: $contextFilter
                                ) {
                                    asBits {
                                        reason
                                        context
                                        value
                                    }
                                }
                            }
                        }
                    """,
                    "variables": {
                        "tokenList": token_list,
                        "contextFilter": context_filter.to_dict(),
                    }
                }
            )
            if response.status_code == 200:
                if "errors" in response.json():
                    return Result(error=response.json()["errors"][0]["message"])
                else:
                    return Result(
                        data=BitCollectionComposer(
                            collections=list(
                                starmap(
                                    lambda tokens, meta: BitCollection(
                                        tokens=tokens,
                                        bits=list(
                                            map(
                                                lambda bit: BitVal(
                                                    reason=bit["reason"],
                                                    context=bit["context"],
                                                    value=bit["value"]
                                                ),
                                                meta["asBits"]
                                            )
                                        )
                                    ),
                                    zip(
                                        token_list,
                                        map(
                                            lambda x: x["meta"], 
                                            response.json()["data"]["tokenListBasedContent"]
                                        )
                                    )
                                )
                            )
                        )
                    )
            else:
                return Result(error=response.text)
        except Exception as e:
            return Result(error=str(e))
