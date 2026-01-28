// ❌ yahan koi import NAHI hoga

export const CONTRACT_ADDRESS = "0x752D9ac8Fd9E67CC415fa3a070e574Fb2640a0E5";

export const CONTRACT_ABI = [
  {
    "inputs": [
      {
        "internalType": "bytes32",
        "name": "_contentHash",
        "type": "bytes32"
      },
      {
        "internalType": "bool",
        "name": "_aiGenerated",
        "type": "bool"
      },
      {
        "internalType": "uint256",
        "name": "_confidence",
        "type": "uint256"
      }
    ],
    "name": "storeRecord",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  }
];
