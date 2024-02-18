# ruff: noqa: F403, F405, E402
from __future__ import annotations
from sharingiscaring.GRPCClient.types_pb2 import *
from sharingiscaring.GRPCClient.queries._SharedConverters import (
    Mixin as _SharedConverters,
)
from sharingiscaring.GRPCClient.CCD_Types import *
from sharingiscaring.enums import NET
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sharingiscaring.GRPCClient import GRPCClient


class Mixin(_SharedConverters):
    def get_anonymity_revokers(
        self: GRPCClient,
        block_hash: str,
        net: Enum = NET.MAINNET,
    ) -> list[CCD_ArInfo]:
        result = []
        blockHashInput = self.generate_block_hash_input_from(block_hash)

        grpc_return_value: [ArInfo] = self.stub_on_net(
            net, "GetAnonymityRevokers", blockHashInput
        )

        for ar in list(grpc_return_value):
            result.append(self.convertArInfo(ar))

        return result
