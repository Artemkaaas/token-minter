import json

from indy.error import IndyError, ErrorCode
from indy import wallet, did, ledger, payment, pool

from src.utils import run_coroutine, PAYMENT_PREFIX


def open_wallet(name: str, key: str) -> int:
    wallet_config = {'id': name}
    wallet_credential = {'key': key}
    try:
        return run_coroutine(wallet.open_wallet(json.dumps(wallet_config), json.dumps(wallet_credential)))
    except IndyError as err:
        if err.error_code == ErrorCode.WalletNotFoundError:
            raise Exception('Wallet not found')
        if err.error_code == ErrorCode.CommonInvalidStructure:
            raise Exception('Invalid Wallet name has been provided')
        if err.error_code == ErrorCode.WalletAccessFailed:
            raise Exception('Invalid key has been provided')
        raise Exception(err.message)


def close_wallet(wallet_handle):
    try:
        run_coroutine(wallet.close_wallet(wallet_handle))
    except IndyError as err:
        raise Exception(err.message)


def open_pool(name: str) -> int:
    try:
        run_coroutine(pool.set_protocol_version(2))
        return run_coroutine(pool.open_pool_ledger(name, None))
    except IndyError as err:
        if err.error_code == ErrorCode.PoolLedgerNotCreatedError:
            raise Exception('Pool not found')
        if err.error_code == ErrorCode.CommonInvalidParam2:
            raise Exception('Invalid Pool name has been provided')
        if err.error_code == ErrorCode.PoolLedgerTimeout:
            raise Exception('Cannot connect to Pool')
        raise Exception(err.message)


def close_pool(pool_handle):
    try:
        run_coroutine(pool.close_pool_ledger(pool_handle))
    except IndyError as err:
        raise Exception(err.message)


def get_stored_dids(wallet_handle) -> list:
    try:
        dids = run_coroutine(did.list_my_dids_with_meta(wallet_handle))
        return json.loads(dids)
    except IndyError as err:
        raise Exception(err.message)


def sign_transaction(wallet_handle: int, did: str, transaction: str) -> str:
    try:
        return run_coroutine(ledger.multi_sign_request(wallet_handle, did, transaction))
    except IndyError as err:
        if err.error_code == ErrorCode.CommonInvalidStructure:
            raise Exception('Invalid Transaction')
        raise Exception(err.message)


def send_transaction(pool_handle: int, transaction: str):
    try:
        response = json.loads(
            run_coroutine(ledger.submit_request(pool_handle, transaction)))

        if response['op'] != 'REPLY':
            raise Exception(response['reason'])
    except IndyError as err:
        if err.error_code == ErrorCode.CommonInvalidStructure:
            raise Exception('Invalid Transaction')
        raise Exception(err.message)


def build_mint_transaction(wallet_handle: int, did: str, payment_address: str, amount: int):
    outputs = [{
        'recipient':
            payment_address if payment_address.startswith(PAYMENT_PREFIX) else PAYMENT_PREFIX + payment_address,
        'amount': amount
    }]

    try:
        return run_coroutine(payment.build_mint_req(wallet_handle, did, json.dumps(outputs), None))
    except IndyError as err:
        if err.error_code == ErrorCode.CommonInvalidStructure:
            raise Exception('Invalid payment address has been provided')
        raise Exception(err.message)
