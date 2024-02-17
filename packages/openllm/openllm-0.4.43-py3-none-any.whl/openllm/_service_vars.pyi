from typing import Dict, Optional

from openllm_core._typing_compat import LiteralSerialisation

model_id: str = ...
model_tag: Optional[str] = ...
adapter_map: Optional[Dict[str, str]] = ...
serialization: LiteralSerialisation = ...
trust_remote_code: bool = ...
