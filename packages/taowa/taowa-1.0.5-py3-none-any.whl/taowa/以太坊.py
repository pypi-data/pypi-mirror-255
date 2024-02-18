# -*- coding: utf-8 -*-
from web3 import Web3
from eth_account import Account
from eth_account.messages import encode_defunct
from decimal import Decimal
import json,re


class 以太坊:
    def __init__(self, 连接=True, rpc=''):
        if 连接:
            url = rpc if rpc else 'https://rpc.ankr.com/bsc'
            self.web3 = Web3(Web3.HTTPProvider(url))
        else:
            self.web3 = Web3
        self.__nft_contract = None
        self.__token_contract = None
        self.__transfer_contract = None

    def 创建钱包(self, 数量=1):
        '返回钱包列表 [(地址,私钥)]'
        钱包列表 = []
        for _ in range(数量):
            account = Account.create()
            privateKey = account.key.hex()
            address = account.address
            钱包列表.append((address, privateKey))
        return 钱包列表

    def 是否已连接(self):
        return self.web3.is_connected()

    def 验证地址(self, 地址):
        '判断是否钱包或合约地址'
        return self.web3.isAddress(地址)

    def 验证地址(self, 地址):
        '判断是否钱包或合约地址'
        return self.web3.is_address(地址)

    def 规范地址(self, 地址):
        '规范地址大小写'
        try:
            return self.web3.to_checksum_address(地址)
        except ValueError:
            # 如果地址不合法，返回None或者抛出异常
            return None

    def 数值_from(self, 数值, 类型):
        '''大数值变小,面值类型参考
        {"wei":1,
         "kwei/babbage/femtoether":1000,
         "mwei/lovelace/picoether":1000000,
         "gwei/shannon/nanoether/nano":1000000000,
         "szabo/microether/micro":1000000000000,
         "finney/milliether/milli":1000000000000000,
         "ether":1000000000000000000,
         "kether/grand":1000000000000000000000,
         "mether":1000000000000000000000000,
         "gether":1000000000000000000000000000,
         "tether":1000000000000000000000000000000}
        '''
        return self.web3.from_wei(数值, 类型)

    def 数值_to(self, 数值, 类型):
        '''小数值变大,面值类型参考
        {"wei":1,
         "kwei/babbage/femtoether":1000,
         "mwei/lovelace/picoether":1000000,
         "gwei/shannon/nanoether/nano":1000000000,
         "szabo/microether/micro":1000000000000,
         "finney/milliether/milli":1000000000000000,
         "ether":1000000000000000000,
         "kether/grand":1000000000000000000000,
         "mether":1000000000000000000000000,
         "gether":1000000000000000000000000000,
         "tether":1000000000000000000000000000000}
        '''
        return self.web3.to_wei(Decimal(str(数值)), 类型)

    def 加载合约(self, 合约地址, ABI):
        'ABI传入文本即可'
        if isinstance(ABI, str):
            ABI = json.loads(ABI)
        合约地址_ = Web3.to_checksum_address(合约地址)
        return self.web3.eth.contract(address=合约地址_, abi=ABI)

    def 获取账户余额(self, 地址):
        '返回当前公链代币余额（如BNB, ETH等）'
        地址_ = Web3.to_checksum_address(地址)
        return self.web3.from_wei(self.web3.eth.get_balance(地址_), 'ether')

    def 获取代币余额(self, 代币合约, 钱包地址, 重复加载=True):
        '返回实际代币余额，数值已经转换过'
        代币合约_ = Web3.to_checksum_address(代币合约)
        钱包地址_ = Web3.to_checksum_address(钱包地址)
        if 重复加载 or (not 重复加载 and not self.__token_contract):
            self.__token_contract = self.web3.eth.contract(address=代币合约_, abi=通用ABI_ERC20)
        代币余额 = self.__token_contract.functions.balanceOf(钱包地址_).call()
        return self.web3.from_wei(代币余额, 'ether')

    def 获取全部NFT编号(self, NFT合约, 钱包地址):
        '返回指定钱包某NFT全部TokenId列表'
        abi = json.loads('[{ "inputs": [{ "internalType": "address", "name": "token", "type": "address" },'
                         '{ "internalType": "address", "name": "_form", "type": "address" }],'
                         ' "name": "tokenOwnerList", '
                         '"outputs": [{ "internalType": "uint256[]", "name": "", "type": "uint256[]" }],'
                         '"stateMutability": "view", "type": "function" }]')
        if not self.__nft_contract:
            合约地址 = Web3.to_checksum_address('0x6Db8A515f24f497890EC4986973E86b534e569a0')
            self.__nft_contract = self.web3.eth.contract(address=合约地址, abi=abi)
        钱包地址_ = Web3.to_checksum_address(钱包地址)
        NFT合约_ = Web3.to_checksum_address(NFT合约)
        return self.__nft_contract.functions.tokenOwnerList(NFT合约_, 钱包地址_).call()

    def 获取指定NFT持有地址(self, 合约, TokenId, 重复加载=True):
        '返回持有人地址'
        合约_ = Web3.to_checksum_address(合约)
        if 重复加载 or (not 重复加载 and not self.__nft_contract):
            self.__nft_contract = self.web3.eth.contract(address=合约_, abi=通用ABI_ERC721)
        return self.__nft_contract.functions.ownerOf(int(TokenId)).call()

    def 获取NFT某地址持有量(self, 合约, 钱包地址, 重复加载=True):
        '返回持有总数'
        合约_ = Web3.to_checksum_address(合约)
        钱包地址_ = Web3.to_checksum_address(钱包地址)
        if 重复加载 or (not 重复加载 and not self.__nft_contract):
            self.__nft_contract = self.web3.eth.contract(address=合约_, abi=通用ABI_ERC721)
        return self.__nft_contract.functions.balanceOf(钱包地址_).call()

    def 获取钱包NFT编号(self, 合约, 钱包地址, 索引=0, 重复加载=True):
        '返回持有总数'
        合约_ = Web3.to_checksum_address(合约)
        钱包地址_ = Web3.to_checksum_address(钱包地址)
        if 重复加载 or (not 重复加载 and not self.__nft_contract):
            self.__nft_contract = self.web3.eth.contract(address=合约_, abi=通用ABI_ERC721)
        return self.__nft_contract.functions.tokenOfOwnerByIndex(钱包地址_, 索引).call()

    def 获取NFT合约信息(self, 合约):
        '返回 项目名称,代号,代币总量'
        信息 = {}
        合约_ = Web3.to_checksum_address(合约)
        contract = self.web3.eth.contract(address=合约_, abi=通用ABI_ERC721)
        信息['名称'] = contract.functions.name().call()
        信息['Token'] = contract.functions.symbol().call()
        信息['总量'] = contract.functions.totalSupply().call()
        return 信息

    def 获取代币价格(self, 代币合约, 交易对合约):
        # ABI 定义
        abi_factory = json.loads('[{"constant":true,"inputs":[{"internalType":"address","name":"","type":"address"},'
                                 '{"internalType":"address","name":"","type":"address"}],"name":"getPair",'
                                 '"outputs":[{"internalType":"address","name":"","type":"address"}],'
                                 '"payable":false,"stateMutability":"view","type":"function"}]')
        abi_pair = json.loads('[{"constant":true,"inputs":[],"name":"getReserves",'
                              '"outputs":[{"internalType":"uint112","name":"_reserve0","type":"uint112"},'
                              '{"internalType":"uint112","name":"_reserve1","type":"uint112"},'
                              '{"internalType":"uint32","name":"_blockTimestampLast","type":"uint32"}],'
                              '"payable":false,"stateMutability":"view","type":"function"}]')

        # 合约地址
        factory_address = self.web3.to_checksum_address('0xca143ce32fe78f1f7019d7d551a6402fc5350c73')
        代币合约_ = self.web3.to_checksum_address(代币合约)
        交易对合约_ = self.web3.to_checksum_address(交易对合约)

        # 创建合约对象
        factory_contract = self.web3.eth.contract(address=factory_address, abi=abi_factory)
        pair_address = factory_contract.functions.getPair(代币合约_, 交易对合约_).call()

        # 检查配对地址是否有效
        if pair_address == self.web3.to_checksum_address('0x0000000000000000000000000000000000000000'):
            return None

        # 查询储备量并计算价格
        pair_contract = self.web3.eth.contract(address=pair_address, abi=abi_pair)
        reserves = pair_contract.functions.getReserves().call()
        return reserves[1] / reserves[0]

    def 获取区块数据(self, 编号或哈希='latest'):
        """通过它们的编号或哈希来查找块，默认为最新"""
        return self.web3.eth.get_block(编号或哈希)

    def 获取最新区块编号(self):
        """获取当前的最新区块编号"""
        return self.web3.eth.block_number

    def 获取nonce(self, 地址):
        """发送交易时需要nonce值"""
        地址_ = self.web3.to_checksum_address(地址)
        return self.web3.eth.get_transaction_count(地址_, 'pending')

    def 导入钱包(self, 私钥):
        """通过私钥导入钱包，获取地址和私钥
        :return: address,key
        """
        account = self.web3.eth.account.from_key(私钥)
        return account.address, account.key.hex()

    def 获取交易详情(self, 交易哈希):
        """如果找不到给定哈希的交易，则此函数将改为返回None"""
        try:
            return self.web3.eth.get_transaction(交易哈希)
        except Exception as e:
            return None

    def 消息签名(self, 签名的内容, 钱包key):
        '一般需要 签名.signature.hex()'
        return self.web3.eth.account.sign_message(encode_defunct(text=签名的内容), private_key=钱包key)

    def 消息签名验证(self, 原签名的内容, signature):
        '返回签名使用的钱包地址'
        return self.web3.eth.account.recover_message(encode_defunct(text=原签名的内容), signature=signature)


    def 估算gas(self, 待估算的交易字典):
        """估算交易所需的gas量。"""
        try:
            return self.web3.eth.estimate_gas(待估算的交易字典)
        except Exception as erro:
            print(f"估算Gas时出现错误：{erro}")
            return None  # 或者返回一个特定的错误标识

    def 获取区块数据(self, 编号或哈希='latest'):
        """通过它们的编号或哈希来查找块，默认为最新"""
        return self.web3.eth.get_block(编号或哈希)

    def 获取最新区块编号(self):
        """获取当前的最新区块编号"""
        return self.web3.eth.block_number

    def 获取nonce(self, 地址):
        """发送交易时需要nonce值"""
        地址_ = self.web3.to_checksum_address(地址)
        return self.web3.eth.get_transaction_count(地址_, 'pending')

    def 导入钱包(self, 私钥):
        """通过私钥导入钱包，获取地址和私钥"""
        account = self.web3.eth.account.from_key(私钥)
        return account.address, account.key.hex()

    def 获取交易详情(self, 交易哈希):
        """如果找不到给定哈希的交易，则此函数将改为返回None"""
        try:
            return self.web3.eth.get_transaction(交易哈希)
        except Exception as e:
            return None

    def 是否为16进制(self, 字符串):
        # 检查字符串是否为有效的16进制，不论是否带0x前缀
        if 字符串.startswith('0x'):
            return re.fullmatch(r'0x[0-9a-fA-F]+', 字符串) is not None
        else:
            return re.fullmatch(r'[0-9a-fA-F]+', 字符串) is not None

    def 发布交易(self, 私钥, From,to, gas=None, gasPrice=None, value=None, data='', nonce=None,chainId=None):
        """返回交易哈希"""
        # 检查data是否为有效的16进制
        if not self.是否为16进制(data) and isinstance(data, str):
            data = Web3.to_hex(text=data)

        参数 = {
            'from': Web3.to_checksum_address(From),
            'to': Web3.to_checksum_address(to),
            'value': 0 if value is None else Web3.to_wei(value, 'ether'),
            'data': data or '',
            'gasPrice': int(gasPrice*1000000000) if gasPrice is not None else self.web3.eth.gas_price
        }
        # 设置链ID
        参数['chainId'] = chainId if chainId else self.web3.eth.chain_id

        # 设置Gas
        参数['gas'] = gas if gas else self.web3.eth.estimate_gas(参数)

        # 设置Nonce
        参数['nonce'] = nonce if nonce is not None else self.web3.eth.get_transaction_count(
            Web3.to_checksum_address(From), 'pending')
        # 尝试发送交易，如遇到nonce太低的异常，则递增nonce并重试
        最大重试次数 = 10
        for i in range(最大重试次数):
            try:
                signed_txn = self.web3.eth.account.sign_transaction(参数, private_key=私钥)
                tx_id = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
                return tx_id.hex()
            except Exception as e:
                if 'nonce too low' in str(e):
                    参数['nonce'] += 1
                else:
                    print(e,参数)
        return ''
        # raise Exception("交易发送失败，超过最大重试次数")

    def 取链ID(self) -> int:
        return self.web3.eth.chain_id

    def 取链上Gas价格(self) -> int:
        '返回的gas跟区块链浏览器的一样 已经被除过的'
        return self.web3.eth.gas_price / 1000000000

    def 交易是否已上链(self, tx) -> int:
        '''
        :param tx: 交易的哈希
        :return: 0.未上链 -1.失败 1.已上链
        '''
        try:
            result = self.web3.eth.get_transaction_receipt(tx)
            if result['blockNumber'] is None:
                return 0
            elif result['status']:
                return 1
            else:
                return -1
        except Exception:
            return 0

    def 解析交易详情(self, tx_hash):
        """
        根据交易哈希解析交易详情。
        :param tx_hash: 交易哈希。
        :return: 包含交易详情的字典，如果交易不存在则返回 None。
        """
        try:
            transaction = self.web3.eth.get_transaction(tx_hash)
            if transaction:
                return {
                    'from': transaction['from'],
                    'to': transaction.get('to'),  # 'to' 字段可能在合约创建交易中不存在
                    'gas': transaction['gas'],
                    'gasPrice': transaction['gasPrice'],
                    'value': transaction['value'],
                    'data': transaction['input'],  # 'data' 字段通常在交易中称为 'input'
                    'nonce': transaction['nonce']
                }
            else:
                return None
        except Exception as e:
            print(f"解析交易时发生错误：{e}")
            return None






通用ABI_ERC20 = json.loads(
    '[{"constant":true,"inputs":[],"name":"name","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_spender","type":"address"},{"name":"_value","type":"uint256"}],"name":"approve","outputs":[{"name":"success","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"totalSupply","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_from","type":"address"},{"name":"_to","type":"address"},{"name":"_value","type":"uint256"}],"name":"transferFrom","outputs":[{"name":"success","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_value","type":"uint256"}],"name":"burn","outputs":[{"name":"success","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"name":"","type":"address"}],"name":"balanceOf","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_from","type":"address"},{"name":"_value","type":"uint256"}],"name":"burnFrom","outputs":[{"name":"success","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"symbol","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_to","type":"address"},{"name":"_value","type":"uint256"}],"name":"transfer","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"_spender","type":"address"},{"name":"_value","type":"uint256"},{"name":"_extraData","type":"bytes"}],"name":"approveAndCall","outputs":[{"name":"success","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"name":"","type":"address"},{"name":"","type":"address"}],"name":"allowance","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"inputs":[{"name":"initialSupply","type":"uint256"},{"name":"tokenName","type":"string"},{"name":"tokenSymbol","type":"string"}],"payable":false,"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":true,"name":"from","type":"address"},{"indexed":true,"name":"to","type":"address"},{"indexed":false,"name":"value","type":"uint256"}],"name":"Transfer","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"owner","type":"address"},{"indexed":true,"name":"spender","type":"address"},{"indexed":false,"name":"value","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"from","type":"address"},{"indexed":false,"name":"value","type":"uint256"}],"name":"Burn","type":"event"}]')
通用ABI_ERC721 = json.loads(
    '[{"constant":true,"inputs":[{"name":"_interfaceID","type":"bytes4"}],"name":"supportsInterface","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"cfoAddress","outputs":[{"name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"_tokenId","type":"uint256"},{"name":"_preferredTransport","type":"string"}],"name":"tokenMetadata","outputs":[{"name":"infoUrl","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"promoCreatedCount","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"name","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_to","type":"address"},{"name":"_tokenId","type":"uint256"}],"name":"approve","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"ceoAddress","outputs":[{"name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"GEN0_STARTING_PRICE","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_address","type":"address"}],"name":"setSiringAuctionAddress","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"totalSupply","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"pregnantKitties","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"_kittyId","type":"uint256"}],"name":"isPregnant","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"GEN0_AUCTION_DURATION","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"siringAuction","outputs":[{"name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_from","type":"address"},{"name":"_to","type":"address"},{"name":"_tokenId","type":"uint256"}],"name":"transferFrom","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"_address","type":"address"}],"name":"setGeneScienceAddress","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"_newCEO","type":"address"}],"name":"setCEO","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"_newCOO","type":"address"}],"name":"setCOO","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"_kittyId","type":"uint256"},{"name":"_startingPrice","type":"uint256"},{"name":"_endingPrice","type":"uint256"},{"name":"_duration","type":"uint256"}],"name":"createSaleAuction","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[],"name":"unpause","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"name":"","type":"uint256"}],"name":"sireAllowedToAddress","outputs":[{"name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"_matronId","type":"uint256"},{"name":"_sireId","type":"uint256"}],"name":"canBreedWith","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"","type":"uint256"}],"name":"kittyIndexToApproved","outputs":[{"name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_kittyId","type":"uint256"},{"name":"_startingPrice","type":"uint256"},{"name":"_endingPrice","type":"uint256"},{"name":"_duration","type":"uint256"}],"name":"createSiringAuction","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"val","type":"uint256"}],"name":"setAutoBirthFee","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"_addr","type":"address"},{"name":"_sireId","type":"uint256"}],"name":"approveSiring","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"_newCFO","type":"address"}],"name":"setCFO","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"_genes","type":"uint256"},{"name":"_owner","type":"address"}],"name":"createPromoKitty","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"secs","type":"uint256"}],"name":"setSecondsPerBlock","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"paused","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[],"name":"withdrawBalance","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"name":"_tokenId","type":"uint256"}],"name":"ownerOf","outputs":[{"name":"owner","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"GEN0_CREATION_LIMIT","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"newContractAddress","outputs":[{"name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_address","type":"address"}],"name":"setSaleAuctionAddress","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"name":"_owner","type":"address"}],"name":"balanceOf","outputs":[{"name":"count","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_v2Address","type":"address"}],"name":"setNewAddress","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"secondsPerBlock","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[],"name":"pause","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"name":"_owner","type":"address"}],"name":"tokensOfOwner","outputs":[{"name":"ownerTokens","type":"uint256[]"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_matronId","type":"uint256"}],"name":"giveBirth","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[],"name":"withdrawAuctionBalances","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"symbol","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"","type":"uint256"}],"name":"cooldowns","outputs":[{"name":"","type":"uint32"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"","type":"uint256"}],"name":"kittyIndexToOwner","outputs":[{"name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_to","type":"address"},{"name":"_tokenId","type":"uint256"}],"name":"transfer","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"cooAddress","outputs":[{"name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"autoBirthFee","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"erc721Metadata","outputs":[{"name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_genes","type":"uint256"}],"name":"createGen0Auction","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"name":"_kittyId","type":"uint256"}],"name":"isReadyToBreed","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"PROMO_CREATION_LIMIT","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_contractAddress","type":"address"}],"name":"setMetadataAddress","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"saleAuction","outputs":[{"name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"_id","type":"uint256"}],"name":"getKitty","outputs":[{"name":"isGestating","type":"bool"},{"name":"isReady","type":"bool"},{"name":"cooldownIndex","type":"uint256"},{"name":"nextActionAt","type":"uint256"},{"name":"siringWithId","type":"uint256"},{"name":"birthTime","type":"uint256"},{"name":"matronId","type":"uint256"},{"name":"sireId","type":"uint256"},{"name":"generation","type":"uint256"},{"name":"genes","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_sireId","type":"uint256"},{"name":"_matronId","type":"uint256"}],"name":"bidOnSiringAuction","outputs":[],"payable":true,"stateMutability":"payable","type":"function"},{"constant":true,"inputs":[],"name":"gen0CreatedCount","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"geneScience","outputs":[{"name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_matronId","type":"uint256"},{"name":"_sireId","type":"uint256"}],"name":"breedWithAuto","outputs":[],"payable":true,"stateMutability":"payable","type":"function"},{"inputs":[],"payable":false,"stateMutability":"nonpayable","type":"constructor"},{"payable":true,"stateMutability":"payable","type":"fallback"},{"anonymous":false,"inputs":[{"indexed":false,"name":"owner","type":"address"},{"indexed":false,"name":"matronId","type":"uint256"},{"indexed":false,"name":"sireId","type":"uint256"},{"indexed":false,"name":"cooldownEndBlock","type":"uint256"}],"name":"Pregnant","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"name":"from","type":"address"},{"indexed":false,"name":"to","type":"address"},{"indexed":false,"name":"tokenId","type":"uint256"}],"name":"Transfer","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"name":"owner","type":"address"},{"indexed":false,"name":"approved","type":"address"},{"indexed":false,"name":"tokenId","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"name":"owner","type":"address"},{"indexed":false,"name":"kittyId","type":"uint256"},{"indexed":false,"name":"matronId","type":"uint256"},{"indexed":false,"name":"sireId","type":"uint256"},{"indexed":false,"name":"genes","type":"uint256"}],"name":"Birth","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"name":"newContract","type":"address"}],"name":"ContractUpgrade","type":"event"},{"constant":true,"inputs":[{"name":"_owner","type":"address"},{"name":"_index","type":"uint256"}],"name":"tokenOfOwnerByIndex","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"}]')

节点_Bsc = [
    'https://rpc.ankr.com/bsc',
    'https://bsc-dataseed.binance.org',
    'https://bsc-dataseed1.binance.org',
    'https://bsc-dataseed2.binance.org',
    'https://bsc-dataseed3.binance.org',
    'https://bsc-dataseed4.binance.org',
    'https://bsc-dataseed2.defibit.io',
    'https://bsc-dataseed3.defibit.io',
    'https://bsc-dataseed4.defibit.io',
    'https://bsc-dataseed2.ninicoin.io',
    'https://bsc-dataseed3.ninicoin.io',
    'https://bsc-dataseed4.ninicoin.io',
    'https://binance.ankr.com/',
    'https://1rpc.io/bnb'
]

节点_Eth = [
    'https://rpc.ankr.com/eth',
    'https://web3.mytokenpocket.vip',
    'https//eth626892d.jccdex.cn',
    'https://api.edennetwork.io/v1/rpc'
]

节点_Ethw = ['https://mainnet.ethereumpow.org',
           'https://rpc2.yayasea.com']
节点_Ftm = ['https://rpc.ankr.com/fantom']
节点_Arb = ['https://rpc.ankr.com/arbitrum']
节点_Optimism = ['https://rpc.ankr.com/optimism']
节点_Avax = ['https://rpc.ankr.com/avalanche']
节点_Tron = ['https://rpc.ankr.com/http/tron']
节点_Near = ['https://rpc.ankr.com/near']
节点_Gno = ['https://rpc.ankr.com/gnosis']
节点_Zks = ['https://rpc.ankr.com/zksync_era']
节点_Base = ['https://rpc.ankr.com/base']
节点_Celo = ['https://rpc.ankr.com/celo']
节点_Scroll = ['https://rpc.ankr.com/scroll']
节点_Sol = ['https://rpc.ankr.com/solana_devnet']
节点_Mnt = ['https://rpc.ankr.com/mantle']
节点_Fil = ['https://rpc.ankr.com/filecoin']
节点_Glmr = ['https://rpc.ankr.com/moonbeam']
节点_One = ['https://rpc.ankr.com/harmony']
节点_Apt = ['https://rpc.ankr.com/http/aptos/v1']
节点_Arbitrum = ['https://rpc.ankr.com/arbitrumnova']
节点_Xdc = ['https://rpc.ankr.com/xdc']
节点_Klay = ['https://rpc.ankr.com/klaytn']
节点_Sys = ['https://rpc.ankr.com/syscoin']
节点_Sei = ['https://rpc.ankr.com/sei']
节点_Chz = ['https://rpc.ankr.com/chiliz']
节点_Btt = ['https://rpc.ankr.com/bttc']
节点_Iotx = ['https://rpc.ankr.com/iotex']
节点_Core = ['https://rpc.ankr.com/core']
节点_Zen = ['https://rpc.ankr.com/horizen_eon']

节点_Heco = [
    'https://http-mainnet.hecochain.com',
    'https//http-mainnet-node.defibox.com',
    'https//http-mainnet-node.huobichain.com/'
]

节点_Polygon = [
    'https://rpc.ankr.com/polygon'
    'https://polygon-rpc.com'
]




