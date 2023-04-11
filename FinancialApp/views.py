from django.shortcuts import render
from django.template import RequestContext
from django.contrib import messages
import pymysql
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage
import os
from datetime import date
import os
import json
from web3 import Web3, HTTPProvider
import ipfsapi
import os
from django.core.files.storage import FileSystemStorage
import pickle
from datetime import datetime

global details, username
details=''
global contract

api = ipfsapi.Client(host='http://127.0.0.1', port=5001)

def readDetails(contract_type):
    global details
    details = ""
    print(contract_type+"======================")
    blockchain_address = 'http://127.0.0.1:9545' #Blokchain connection IP
    web3 = Web3(HTTPProvider(blockchain_address))
    web3.eth.defaultAccount = web3.eth.accounts[0]
    compiled_contract_path = 'FinancialContract.json' #financial contract code
    deployed_contract_address = '0x6901bE3b7C14cfe61357047bde7f047FA79b01a0' #hash address to access student contract
    with open(compiled_contract_path) as file:
        contract_json = json.load(file)  # load contract info as JSON
        contract_abi = contract_json['abi']  # fetch contract's abi - necessary to call its functions
    file.close()
    contract = web3.eth.contract(address=deployed_contract_address, abi=contract_abi) #now calling contract to access data
    if contract_type == 'adduser':
        details = contract.functions.getUser().call()
    if contract_type == 'addproduct':
        details = contract.functions.getProducts().call()
    if contract_type == 'addcart':
        details = contract.functions.getCart().call()
    if contract_type == 'addwallet':
        details = contract.functions.getWallets().call()
    if len(details) > 0:
        if 'empty' in details:
            details = details[5:len(details)]       
    print(details)    

def saveDataBlockChain(currentData, contract_type):
    global details
    global contract
    details = ""
    blockchain_address = 'http://127.0.0.1:9545'
    web3 = Web3(HTTPProvider(blockchain_address))
    web3.eth.defaultAccount = web3.eth.accounts[0]
    compiled_contract_path = 'FinancialContract.json' #ecommerce contract file
    deployed_contract_address = '0x6901bE3b7C14cfe61357047bde7f047FA79b01a0' #contract address
    with open(compiled_contract_path) as file:
        contract_json = json.load(file)  # load contract info as JSON
        contract_abi = contract_json['abi']  # fetch contract's abi - necessary to call its functions
    file.close()
    contract = web3.eth.contract(address=deployed_contract_address, abi=contract_abi)
    readDetails(contract_type)
    if contract_type == 'adduser':
        details+=currentData
        msg = contract.functions.addUser(details).transact()
        tx_receipt = web3.eth.waitForTransactionReceipt(msg)
    if contract_type == 'addproduct':
        details+=currentData
        msg = contract.functions.addProducts(details).transact()
        tx_receipt = web3.eth.waitForTransactionReceipt(msg)
    if contract_type == 'addcart':
        details+=currentData
        msg = contract.functions.addCart(details).transact()
        tx_receipt = web3.eth.waitForTransactionReceipt(msg)
    if contract_type == 'addwallet':
        details+=currentData
        msg = contract.functions.addWallets(details).transact()
        tx_receipt = web3.eth.waitForTransactionReceipt(msg)

def ViewProviders(request):
    if request.method == 'GET':
        global details
        user = ''
        with open("session.txt", "r") as file:
            for line in file:
                user = line.strip('\n')
        file.close()
        output = '<table border=1 align=center>'
        output+='<tr><th><font size=3 color=black>Username</font></th>'
        output+='<th><font size=3 color=black>Contact No</font></th>'
        output+='<th><font size=3 color=black>Email ID</font></th>'
        output+='<th><font size=3 color=black>Address</font></th>'
        output+='<th><font size=3 color=black>User Type</font></th></tr>'
        readDetails("adduser")
        rows = details.split("\n")
        for i in range(len(rows)-1):
            arr = rows[i].split("#")
            if arr[0] == 'signup' and arr[6] == 'Service Provider':
                output+='<tr><td><font size=3 color=black>'+arr[1]+'</font></td>'
                output+='<td><font size=3 color=black>'+arr[3]+'</font></td>'
                output+='<td><font size=3 color=black>'+arr[4]+'</font></td>'
                output+='<td><font size=3 color=black>'+arr[5]+'</font></td>'
                output+='<td><font size=3 color=black>'+arr[6]+'</font></td></tr>'
        output+="</table><br/><br/><br/><br/><br/><br/>"
        context= {'data':output}
        return render(request, 'ViewProviders.html', context)     
        

def getAmount():
    global username
    readDetails("addwallet")
    deposit = 0
    wd = 0
    rows = details.split("\n")
    for i in range(len(rows)-1):
        arr = rows[i].split("#")
        if arr[0] == username:
            if arr[3] == 'Self Deposit':
                deposit = deposit + float(arr[1])
            else:
                wd = wd + float(arr[1])
    deposit = deposit - wd
    return deposit

def AddMoney(request):
    if request.method == 'GET':
        global username
        output = '<tr><td><font size="3" color="black">Username</td><td><input type="text" name="t1" size="20" value="'+username+'" readonly/></td></tr>'
        output += '<tr><td><font size="3" color="black">Available&nbsp;Balance</td><td><input type="text" name="t2" size="20" value='+str(getAmount())+' readonly/></td></tr>'
        context= {'data1':output}
        return render(request, 'AddMoney.html', context) 

def AddMoneyAction(request):
    global details
    if request.method == 'POST':
        username = request.POST.get('t1', False)
        amount = request.POST.get('t3', False)
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        data = username+"#"+amount+"#"+str(timestamp)+"#Self Deposit\n"
        saveDataBlockChain(data,"addwallet")
        context= {'data':'Money added to user wallet '+username}
        return render(request, 'UserScreen.html', context)

def index(request):
    if request.method == 'GET':
       return render(request, 'index.html', {})    

def BrowseProducts(request):
    if request.method == 'GET':
        output = '<tr><td><font size="" color="black">Product&nbsp;Name</font></td><td><select name="t1">'
        readDetails("addproduct")
        rows = details.split("\n")
        for i in range(len(rows)-1):
            arr = rows[i].split("#")
            if arr[0] == 'addproduct':
                output+='<option value="'+arr[2]+'">'+arr[2]+'</option>'
        output+="</select></td></tr>"
        context= {'data1':output}
        return render(request, 'BrowseProducts.html', context)

def Login(request):
    if request.method == 'GET':
       return render(request, 'Login.html', {})
    
def ViewOrders(request):
    if request.method == 'GET':
        global details
        user = ''
        with open("session.txt", "r") as file:
            for line in file:
                user = line.strip('\n')
        file.close()
        output = '<table border=1 align=center>'
        output+='<tr><th><font size=3 color=black>Product Name</font></th>'
        output+='<th><font size=3 color=black>Customer Name</font></th>'
        output+='<th><font size=3 color=black>Contact No</font></th>'
        output+='<th><font size=3 color=black>Email ID</font></th>'
        output+='<th><font size=3 color=black>Address</font></th>'
        output+='<th><font size=3 color=black>Ordered Date</font></th></tr>'
        readDetails("addcart")
        rows = details.split("\n")
        for i in range(len(rows)-1):
            arr = rows[i].split("#")
            if arr[0] == 'bookorder':
                print(arr[2]+" "+user)
                details = arr[3].split(",")
                pid = arr[1]
                user = arr[2]
                book_date = arr[4]
                output+='<tr><td><font size=3 color=black>'+pid+'</font></td>'
                output+='<td><font size=3 color=black>'+user+'</font></td>'
                output+='<td><font size=3 color=black>'+details[0]+'</font></td>'
                output+='<td><font size=3 color=black>'+details[1]+'</font></td>'
                output+='<td><font size=3 color=black>'+details[2]+'</font></td>'
                output+='<td><font size=3 color=black>'+str(book_date)+'</font></td></tr>'
        output+="</table><br/><br/><br/><br/><br/><br/>"
        context= {'data':output}
        return render(request, 'ViewOrders.html', context)     

def Register(request):
    if request.method == 'GET':
       return render(request, 'Register.html', {})

def AddProduct(request):
    if request.method == 'GET':
       return render(request, 'AddProduct.html', {})

def BookOrders(request):
    if request.method == 'GET':
        global details
        provider = request.GET['farmer']
        product = request.GET['crop']
        amount = request.GET['amount']
        output = '<tr><td><font size="3" color="black">Service&nbsp;Provider</td><td><input type="text" name="t1" size="20" value="'+provider+'" readonly/></td></tr>'
        output += '<tr><td><font size="3" color="black">Product</td><td><input type="text" name="t2" size="20" value="'+product+'" readonly/></td></tr>'
        output += '<tr><td><font size="3" color="black">Amount</td><td><input type="text" name="t3" size="20" value='+amount+' readonly/></td></tr>'
        context= {'data1':output}
        return render(request, 'BookOrders.html', context)   

def BookOrder(request):
    if request.method == 'POST':
        global details, username
        pid = request.POST.get('t2', False)
        amount = request.POST.get('t3', False)
        payment_option = request.POST.get('t4', False)
        balance = getAmount()
        output = "Insufficient Balance is Wallet"
        details = ""
        if float(amount) < balance and payment_option == 'Wallet':
            readDetails("adduser")
            rows = details.split("\n")
            output = 'Your Order details Updated & payment done from wallet<br/>'
            for i in range(len(rows)-1):
                arr = rows[i].split("#")
                if arr[0] == "signup":
                    if arr[1] == username:
                        details = arr[3]+","+arr[4]+","+arr[5]
                        break
        if payment_option == 'Card':
            readDetails("adduser")
            rows = details.split("\n")
            output = 'Your Order details Updated & payment done from card<br/>'
            for i in range(len(rows)-1):
                arr = rows[i].split("#")
                if arr[0] == "signup":
                    if arr[1] == user:
                        details = arr[3]+","+arr[4]+","+arr[5]
                        break
        if output != "Insufficient Balance is Wallet":
            today = date.today()            
            data = "bookorder#"+pid+"#"+username+"#"+details+"#"+str(today)+"\n"
            saveDataBlockChain(data,"addcart")
            data = username+"#"+amount+"#"+str(today)+"#Paid Towards "+pid+" purchased\n"
            saveDataBlockChain(data,"addwallet")
        context= {'data':output}
        return render(request, 'UserScreen.html', context)      

def SearchProductAction(request):
    if request.method == 'POST':
        ptype = request.POST.get('t1', False)
        output = '<table border=1 align=center>'
        output+='<tr><th><font size=3 color=black>Service Provider Name</font></th>'
        output+='<th><font size=3 color=black>Product Name</font></th>'
        output+='<th><font size=3 color=black>Price</font></th>'
        output+='<th><font size=3 color=black>Quantity</font></th>'
        output+='<th><font size=3 color=black>Description</font></th>'
        output+='<th><font size=3 color=black>Image</font></th>'
        output+='<th><font size=3 color=black>Purchase Product</font></th></tr>'
        readDetails("addproduct")
        rows = details.split("\n")
        for i in range(len(rows)-1):
            arr = rows[i].split("#")
            print("my=== "+str(arr[0])+" "+arr[1]+" "+arr[2]+" "+ptype)
            if arr[0] == 'addproduct':
                if arr[2] == ptype:
                    output+='<tr><td><font size=3 color=black>'+arr[1]+'</font></td>'
                    output+='<td><font size=3 color=black>'+arr[2]+'</font></td>'
                    output+='<td><font size=3 color=black>'+str(arr[3])+'</font></td>'
                    output+='<td><font size=3 color=black>'+str(arr[4])+'</font></td>'
                    output+='<td><font size=3 color=black>'+arr[5]+'</font></td>'
                    content = api.get_pyobj(arr[6])
                    content = pickle.loads(content)
                    if os.path.exists('FinancialApp/static/product.png'):
                        os.remove('FinancialApp/static/product.png')
                    with open('FinancialApp/static/product.png', "wb") as file:
                        file.write(content)
                    file.close()
                    output+='<td><img src="/static/product.png" width="200" height="200"></img></td>'
                    output+='<td><a href=\'BookOrders?farmer='+arr[1]+'&crop='+arr[2]+'&amount='+str(arr[3])+'\'><font size=3 color=black>Click Here</font></a></td></tr>'
        output+="</table><br/><br/><br/><br/><br/><br/>"
        context= {'data':output}
        return render(request, 'SearchProducts.html', context)              
        
    
def AddProductAction(request):
    if request.method == 'POST':
        cname = request.POST.get('t1', False)
        qty = request.POST.get('t2', False)
        price = request.POST.get('t3', False)
        desc = request.POST.get('t4', False)
        image = request.FILES['t5'].read()
        imagename = request.FILES['t5'].name
        user = ''
        with open("session.txt", "r") as file:
            for line in file:
                user = line.strip('\n')
        file.close()
        myfile = pickle.dumps(image)
        hashcode = api.add_pyobj(myfile)
        data = "addproduct#"+user+"#"+cname+"#"+price+"#"+qty+"#"+desc+"#"+hashcode+"\n"
        saveDataBlockChain(data,"addproduct")
        context= {'data':"Product details saved and IPFS image storage hashcode = "+hashcode}
        return render(request, 'AddProduct.html', context)
        
   
def Signup(request):
    if request.method == 'POST':
        username = request.POST.get('username', False)
        password = request.POST.get('password', False)
        contact = request.POST.get('contact', False)
        email = request.POST.get('email', False)
        address = request.POST.get('address', False)
        usertype = request.POST.get('type', False)
        record = 'none'
        readDetails("adduser")
        rows = details.split("\n")
        for i in range(len(rows)-1):
            arr = rows[i].split("#")
            if arr[0] == "signup":
                if arr[1] == username:
                    record = "exists"
                    break
        if record == 'none':
            data = "signup#"+username+"#"+password+"#"+contact+"#"+email+"#"+address+"#"+usertype+"\n"
            saveDataBlockChain(data,"adduser")
            context= {'data':'Signup process completd and record saved in Blockchain'}
            return render(request, 'Register.html', context)
        else:
            context= {'data':username+'Username already exists'}
            return render(request, 'Register.html', context)    



def UserLogin(request):
    if request.method == 'POST':
        global username
        username = request.POST.get('username', False)
        password = request.POST.get('password', False)
        usertype = request.POST.get('type', False)
        status = 'none'
        readDetails("adduser")
        rows = details.split("\n")
        for i in range(len(rows)-1):
            arr = rows[i].split("#")
            if arr[0] == "signup":
                if arr[1] == username and arr[2] == password and arr[6] == usertype:
                    status = 'success'
                    break
        if status == 'success' and usertype == 'Service Provider':
            file = open('session.txt','w')
            file.write(username)
            file.close()
            context= {'data':"Welcome "+username}
            return render(request, 'ServiceProviderScreen.html', context)
        elif status == 'success' and usertype == 'User':
            file = open('session.txt','w')
            file.write(username)
            file.close()
            context= {'data':"Welcome "+username}
            return render(request, 'UserScreen.html', context)
        else:
            context= {'data':'Invalid login details'}
            return render(request, 'Login.html', context)            


        
        



        
            
