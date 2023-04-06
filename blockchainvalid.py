import os
import blockchain
import copy

def  blockchainvalid(bc):
    os.system('cls')

    if bc.is_chain_valid():
        input("blockchain was not modified, still works")
    
    else: 
        input("blockchain was modified")
    
    

    while True:
        os.system('cls')
        print("test if chain is valid works?")
        choice = input("Please select an option y-n): ")
        if choice == 'y':
            
            bc1 = copy.deepcopy(bc)
            bc1.chain[1]["article title"]="hello mars"
            os.system('cls')
            print(bc1.chain[1])
            input("check modified block")
            
            if bc1.is_chain_valid():
                input("blockchain was not modified")
            else: 
                input("blockchain was modified")
                

        elif choice == 'n':
            break
        
        else:
            print("Invalid choice. Please try again.")

