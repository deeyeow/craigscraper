import smtplib

def notify_user(names_found, prices_found, links_found, price_lo):

    # creates SMTP session 
    s = smtplib.SMTP('smtp.gmail.com', 587) 
    
    # start TLS for security 
    s.starttls() 
    
    # Authentication 
    s.login('thisismyleaguethrowaway@gmail.com', 'qyhxaj-vIcwy3-pebcyq') 
    
    # message to be sent 
    message = 'Found ' + str(len(names_found)) + ' items under $' + str(price_lo) + '\n'
    for i in range(len(names_found)):
        message = message + '\n' + names_found[i] + '\n' + 'Price: ' + prices_found[i] + '\n' + links_found[i] +'\n'
    
    # sending the mail 
    s.sendmail('thisismyleaguethrowaway@gmail.com', 'craigslistmaster123@gmail.com', message) 
    
    # terminating the session 
    s.quit() 