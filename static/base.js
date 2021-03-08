
/** ANTI-CSRF CODE **/
      let csrf_token = document.querySelector("meta[name='csrf_token']").getAttribute("content");
      axios.defaults.headers.post['anti-csrf-token'] = csrf_token;
      axios.defaults.headers.put['anti-csrf-token'] = csrf_token;
      axios.defaults.headers.delete['anti-csrf-token'] = csrf_token;
      axios.defaults.headers.patch['anti-csrf-token'] = csrf_token;
  
      // Axios does not create an object for TRACE method by default, and has to be created manually.
      axios.defaults.headers.trace = {}
      axios.defaults.headers.trace['anti-csrf-token'] = csrf_token
  
      /// this code is from Cross-Site Request Forgery Prevention Website
      // https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html#use-of-custom-request-headers
   /////////////////////////////////////////////////////////////////////////////////////
   

      
   