#!/usr/bin/env python3
"""
Real EcoFlow protobuf parser that extracts actual device data.
"""

import struct
import logging
from google.protobuf.json_format import MessageToDict
from typing import Dict, Any, Optional

# protoc --proto_path=. --python_out=. ./common.proto ./pr705.proto ./pd335_bms_bp.proto
import common_pb2, pr705_pb2, pd335_bms_bp_pb2

LOG = logging.getLogger(__name__)

class EcoFlowProtobufParser:
    """Parser for EcoFlow binary protobuf messages."""
    
    def decode(self, binary_data: bytes, device_serial: str) -> Optional[Dict[str, Any]]:
        """Parse binary protobuf message and extract real device data."""

        try:
            LOG.debug(f"📨 Parsing message for {device_serial} ({len(binary_data)} bytes)")
            
            sender_msg = common_pb2.Send_Header_Msg()
            sender_msg.ParseFromString(binary_data)
            
            # the encapsuled payload data
            pdata = sender_msg.msg[0].pdata

            if sender_msg.msg[0].enc_type:
                pdata = bytearray(pdata)
                for i in range(len(pdata)):
                    pdata[i] = (pdata[i] ^ sender_msg.msg[0].seq) & 0xFF
                
            if sender_msg.msg[0].cmd_func == 32 and sender_msg.msg[0].cmd_id == 50:
                m = pd335_bms_bp_pb2.BMSHeartBeatReport()
                m.ParseFromString(pdata)
                params = MessageToDict(m)
                return params

            elif sender_msg.msg[0].cmd_func == 254 and sender_msg.msg[0].cmd_id == 21:
                m = pr705_pb2.DisplayPropertyUpload()
                m.ParseFromString(pdata)
                params = MessageToDict(m)
                return params

            else:
                d = pdata.hex()
                LOG.debug(f"🛑 seq={sender_msg.msg[0].seq} cmd_func={sender_msg.msg[0].cmd_func} cmd_id={sender_msg.msg[0].cmd_id} pdata={d}")
            
            return None
            
        except Exception as e:
            LOG.error(f"❌ Failed to parse message for {device_serial}: {e}")
            return None
