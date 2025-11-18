// Inject CSRF token automatically into same-origin unsafe requests
(function(){
  function getCookie(name){
    var m = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
    return m ? decodeURIComponent(m.pop()) : null;
  }
  var _fetch = window.fetch;
  window.fetch = function(input, init){
    try{
      init = init || {};
      var method = (init.method || 'GET').toUpperCase();
      var unsafe = method === 'POST' || method === 'PUT' || method === 'PATCH' || method === 'DELETE';
      var url = (typeof input === 'string') ? input : (input && input.url) || '';
      var sameOrigin = !/^https?:\/\//i.test(url) || url.indexOf(location.origin) === 0 || url.charAt(0) === '/';
      if (unsafe && sameOrigin){
        init.headers = init.headers || {};
        var headers = init.headers;
        // Normalize to plain object
        if (headers instanceof Headers){
          if (!headers.has('X-CSRFToken')){
            headers.set('X-CSRFToken', getCookie('csrftoken'));
          }
        } else {
          if (!('X-CSRFToken' in headers)){
            headers['X-CSRFToken'] = getCookie('csrftoken');
          }
        }
        if (!('credentials' in init)){
          init.credentials = 'same-origin';
        }
      }
    }catch(e){ /* noop */ }
    return _fetch(input, init).then(function(resp){
      try{
        if (resp && resp.status === 403) {
          // Intentar detectar texto de CSRF de Django
          var ct = resp.headers.get('Content-Type') || '';
          if (ct.indexOf('text/html') !== -1) {
            if (typeof window.showToast === 'function') {
              window.showToast('Error de seguridad (CSRF). Recargá la página e iniciá sesión si es necesario.', 'error', 6000);
            } else {
              alert('Error de seguridad (CSRF). Recargá la página e iniciá sesión si es necesario.');
            }
          }
        }
      } catch (e) { /* noop */ }
      return resp;
    });
  };
})();
