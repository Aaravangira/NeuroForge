// Dashboard loader
async function loadDashboard(){
    try{
        const response = await fetch("/api/dashboard", {headers:{"Accept":"application/json"}});
        if(!response.ok) throw new Error(`Dashboard API returned ${response.status}`);
        const payload = await response.json();
        if(!payload.success) return;

        const data = payload.data || {};
        const invoiceCount = document.getElementById("invoiceCount");
        const totalAmount = document.getElementById("totalAmount");
        if(invoiceCount) invoiceCount.textContent = Number(data.total_invoices || 0).toLocaleString();
        if(totalAmount) totalAmount.textContent = "₹" + Number(data.total_amount || 0).toLocaleString("en-IN", {maximumFractionDigits:2});

        // The current dashboard API returns summary data only. Keep the table empty
        // until a recent-invoices endpoint is wired in a later backend phase.
        loadRecentInvoices([]);
    }catch(error){
        console.error("Dashboard loading failed:", error);
    }
}

function loadRecentInvoices(invoices){
    const tbody=document.getElementById("recentInvoices");
    if(!tbody) return;
    tbody.innerHTML="";
    if(!invoices || invoices.length===0){
        tbody.innerHTML=`<tr><td colspan="5"><div class="table-empty"><div class="empty-mini-icon"><i class="bi bi-inbox"></i></div><strong>No invoices yet</strong><span>Processed invoices will appear here.</span></div></td></tr>`;
        return;
    }
    invoices.slice(0,5).forEach(invoice=>{
        tbody.innerHTML += `<tr><td>${invoice.vendor_name||"-"}</td><td>${invoice.invoice_number||"-"}</td><td>${invoice.invoice_date||"-"}</td><td>₹${Number(invoice.grand_total||0).toLocaleString("en-IN")}</td><td><span class="status">Processed</span></td></tr>`;
    });
}

const refreshButton=document.getElementById("refreshDashboard");
if(refreshButton) refreshButton.addEventListener("click", loadDashboard);
document.addEventListener("DOMContentLoaded", loadDashboard);
