function getCookie(name){
  const m = document.cookie.match('(?:^|; )' + name.replace(/([.$?*|{}()\[\]\\\/\+^])/g, '\\$1') + '=([^;]*)');
  return m ? decodeURIComponent(m[1]) : undefined;
}

async function exportReportToPDF(url, params){
  try{
    const csrftoken = getCookie('csrftoken');
    const resp = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(csrftoken ? { 'X-CSRFToken': csrftoken } : {})
      },
      body: JSON.stringify(params),
      credentials: 'include'
    });
    if(!resp.ok){
      const msg = await resp.text();
      console.error('Error exportando', msg);
      return { error: msg, status: resp.status };
    }
    return await resp.json();
  }catch(err){
    console.error(err);
    return { error: String(err) };
  }
}

function downloadPDF(url){
  const a=document.createElement('a');
  a.href=url; a.download='reporte.pdf'; a.click();
}

function showExportProgress(){
  // Placeholder sencillo
  console.log('Generando PDF...');
}
