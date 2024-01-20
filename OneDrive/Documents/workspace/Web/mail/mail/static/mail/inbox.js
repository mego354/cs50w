document.addEventListener('DOMContentLoaded', function() {

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', compose_email);

  // By default, load the inbox
  load_mailbox('inbox');

  // handling sending the email
  document.querySelector('#compose-form').onsubmit = sending;
  
});

function compose_email() {

  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#email-open').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';

  // Clear out composition fields
  document.querySelector('#compose-recipients').value = '';
  document.querySelector('#compose-subject').value = '';
  document.querySelector('#compose-body').value = '';
}

function load_mailbox(mailbox) {
  
  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';
  document.querySelector('#email-open').style.display = 'none';


  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;

  // get the emails
  fetch(`/emails/${mailbox}`)
  .then(response => response.json())
  .then(emails => {
      // Print emails
      console.log(emails);

      // ... do something else with emails ...
      emails.forEach(email => {

        const element = document.createElement('div');
        element.className = "each_email"

        if (email.read) {
          element.style.backgroundColor = "rgba(141, 146, 141, 0.1)";
        }

        element.innerHTML = `
          <div>
          <h5><strong>${email.sender}</strong></h5>
          <h5>${email.subject}</h5>
          </div>
          <div>
          <small class="text-muted">${email.timestamp}</small>


          </div>
        `;

        element.addEventListener('click', () => open_email(email.id, mailbox)) 
        document.querySelector('#emails-view').append(element);     
      });

  });
}


function sending(event) {
  event.preventDefault()

  let recipients = document.querySelector('#compose-recipients').value
  let subject = document.querySelector('#compose-subject').value
  let body = document.querySelector('#compose-body').value
  
  fetch('/emails', {
    method: 'POST',
    body: JSON.stringify({
        recipients: recipients,
        subject: subject,
        body: body
    })
  })
  .then(response => response.json())
  .then(result => {
      // Print result
      console.log(result);
  })
   .then(() => {
    load_mailbox('sent');
  })
}

function open_email(email_id, mailbox) {
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#email-open').style.display = 'block';

  fetch(`/emails/${email_id}`)
  .then(response => response.json())
  .then(email => {
    // Print emails
    console.log(email);

    // ... do something else with emails ...
    document.querySelector('#email-open').innerHTML = `
    <div class="card">
    <div class="card-body">
    <h5 class="card-title"><strong>From: </strong>${email.sender}</h5>
    <h5 class="card-title"><strong>To: </strong>${email.recipients}</h5>
    <h5 class="card-title"><strong>Subject: </strong>${email.subject}</h5>
    <h5 class="card-title"><strong>Timestamp: </strong>${email.timestamp}</h5>
    </div>
    </div>
    <div class="email_body">
    <h5>${email.body}</h5>
    </div>
    
    `;
    const buttons = document.createElement('div');
    buttons.className = "buttons";
    buttons.id = "buttons";
    
    const button2 = document.createElement('button');
    button2.className = "btn btn-md btn-outline-primary";
    button2.innerHTML = "Reply"
    button2.addEventListener('click', () => reply(email.sender, email.subject, email.timestamp, email.body));
    buttons.append(button2)




    if (mailbox !== "sent") {
      const button = document.createElement('button');
      button.className = "btn btn-md btn-outline-info";


      if (email.archived) {
        button.innerHTML = "Un-archive";
      }
      else {
        button.innerHTML = "Archive";

      }
      buttons.append(button)
      button.addEventListener('click', () => change_archive(email.archived, email.id));
    
  }
  document.querySelector('#email-open').append(buttons)

  

  });
  

  fetch(`/emails/${email_id}`, {
    method: 'PUT',
    body: JSON.stringify({
        read: true
    })
  })
  
  

}

function change_archive(archive, email_id) {
  fetch(`/emails/${email_id}`, {
    method: 'PUT',
    body: JSON.stringify({
      archived: !archive
    })
  })
  .then(() => {
    load_mailbox('inbox');
  })

}

function reply(sender, subject, timestamp, body) {
  compose_email();
  document.querySelector('#compose-recipients').value = sender;
  document.querySelector('#compose-body').value = `On ${timestamp} ${sender} wrote: ${body} `;
  let start = ""
  for (let i = 0; i < 3; i++) {
    start += subject[i];
  }

  if (start === "Re:") {
    document.querySelector('#compose-subject').value = subject;
  }
  else {
    document.querySelector('#compose-subject').value = `Re: ${subject}`;
  }
}

