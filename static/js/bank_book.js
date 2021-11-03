
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does $(this) cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
let job_id = []

  $('#cord').change(function(){
    var cord = $(this).val()
    
    if (cord=='COLLECT'){
      $('.collect-item').css('display', 'block')
    }
    else{
      $('.collect-item').css('display', 'none')
    }
  })

  $(document).ready(function(){
  $("#myInput").on("keyup", function() {
    var value = $(this).val().toLowerCase();
    $("#myTable tr").filter(function() {
      $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1)
    });
  });
});

  $('.client').click(function(){
    const client_id= $(this).attr("client_id")
    let client_name = "Client:" + $(this).html()

     $.ajax(
    {
        type:"GET",
        url: "/client_details_gen",
        
        data:{
                 client_id:client_id
        },
        dataType:"json",
        // headers: { "X-CSRFToken": getCookie("csrftoken") },
        success: function( data ) 
        {

          let data_job = data.data
          // console.log(data_job.job_id)
          $('#collect-div').css('display','none')
          $('#jobList').empty()
          let tr = document.createElement('tr')
          let th1 = document.createElement('th')
          let th2 = document.createElement('th')
          let th3 = document.createElement('th')
            $(th1).append("Job No.")
            $(th2).append("Sales")
            $(th3).append("Recieved")
            $(tr).append(th1)
            $(tr).append(th2)
            $(tr).append(th3)
          $('#jobList').html(client_name)
          $('#jobList').append(tr)
          for(i = 0; i<data_job.length; i++){
            let tr = document.createElement('tr')
            let td1 = document.createElement('td')
            let td2 = document.createElement('td')
            let td3 = document.createElement('td')
            let elm= document.createElement('button')
            $(elm).addClass("jobsIdButton")
            $(elm).attr('data-added','false')
            $(elm).attr('data-job-id',data_job[i].job_id)
            $(elm).html(data_job[i].job_no)
            $(td1).append(elm)
            $(td2).append(data_job[i].sales)
            $(td3).append(data_job[i].recieved)
            $(tr).append(td1)
            $(tr).append(td2)
            $(tr).append(td3)
            $('#jobList').append(tr)
          }

        }
     })
  });

  $('#jobList').on('click','.jobsIdButton',function(){
    // console.log($(this).attr('class'))
    let data_added = $(this).attr('data-added')
    let data_job_id = $(this).attr('data-job-id')
    // console.log(data_job_id)
    if (data_added == 'false'){
          job_id.push(data_job_id)
          // console.log(job_id)
          $(this).parent().parent().css("background","red")
          // $(':nth-child(2)',this.parent().parent()).css("background","white")
          let input = document.createElement('input')
          $(input).addClass('inputItem')
          
          $(input).val($(this).parent().next().next().html())
          $(input).attr('type','number')
          $(input).attr('name','jobRecieved')
          $(input).attr('data-job-id', data_job_id)
          $(this).parent().parent().append(input)
          $(this).attr('data-added','true')
        }
    else{
      job_id.splice(job_id.indexOf(data_job_id),1)
      // console.log(job_id)
      $(this).parent().parent().find('.inputItem').remove()
      $(this).parent().parent().css("background","white")
      $(this).attr('data-added','false')
    }
});

  $('#submit').click(function(){
    let formData = {}
    let formReady ="True"
    $('.inputItem').map(function(){
      if ($(this).attr("name")=="cord"){
        if ($(this).val() =="_______"){
          console.log("select a method")
          $(this).parent().append("<h5>*select a method</h5>")
          formReady = "False"
        }
        else{
          formData.cord = $(this).val()

        
        }

      }

       else if ($(this).attr("name")=="date"){
         if ($(this).val() ==""){
          console.log("select a Date")
          $(this).parent().append("<h5>*select a Date</h5>")
          formReady = "False"
        }
        else{
          formData.date = $(this).val()
    
        }
      }

      else if ($(this).attr("name")=="prtc"){

          formData.prtc = $(this).val()
    
        
        
      }
      else if ($(this).attr("name")=="chq_no"){
         formData.chq_no = $(this).val()
      }
      else if ($(this).attr("name")=="chq_date"){
        if ($(this).val() ==""){
          formData.chq_date = "1111-01-01"
        }
          else{
         formData.chq_date = $(this).val()}
      }
      else if ($(this).attr("name")=="bank"){
         formData.bank = $(this).val()
      }
      else if ($(this).attr("name")=="amount"){
        if ($(this).val() ==""){
          console.log("Fill the Entity")
          $(this).parent().append("<h5>*Fill the Entity</h5>")
          formReady = "False"
        }
        else{
          formData.amount = $(this).val()
    
        }
        
      }
      else if ($(this).attr("name")=="jobRecieved"){
        if ($(this).val() ==""){
          console.log("Put any value")
          $(this).parent().append("<h5>*Put any value</h5>")
          formReady = "False"
        }
        else{

      formData[$(this).attr('data-job-id')] = $(this).val()
    }
         
      }
    })
    let jobs_str = ""
    if (job_id.length>=1){
      jobs_str = job_id[0]

    }
    for(i=1; i<job_id.length;i++){
      jobs_str = jobs_str +"," + job_id[i]
    }

      formData.jobs = jobs_str

    console.log(formData)
 if (formReady == "True"){
  $.ajax(
    {
        type:"POST",
        url: "/client_details_gen/",
        
        data:formData,
        dataType:"json",
        // contentType: "application/json; charset=uft-8",
        headers: { "X-CSRFToken": getCookie("csrftoken") },
        success: function( data ) 
        {
          $('body').html(data.html)
          $("#messageBox").css("display","block")
          // let button = document.createElement('button')
          // $(button).html('-')
          // $(button).attr('id',"messageBoxOut")
          // $('#messageBox').append(button)
         
          }

        })
     
 }
  })

  $("#messageBoxOut").click(function(){
    $(this).parent().find('h4').remove()
    $(this).parent().css("display","none")
  })

  $('#makePdf').click(function(){
    var rpage = document.body.innerHTML
    var prcont = document.getElementById("toprint").innerHTML
    
    
    document.body.innerHTML = prcont
    var tr = document.getElementsByTagName("tr")
    for(i=0; i<tr.length; i++){
      if (i==0){
        tr[i].getElementsByTagName("th")[9].style.display ="none"
        tr[i].getElementsByTagName("th")[10].style.display ="none"
      }
      else{
      tr[i].getElementsByTagName("td")[9].style.display ="none"
      tr[i].getElementsByTagName("td")[10].style.display ="none"

    }
      }
    window.print()
    
  })

   function myFunction() {
  var str1 = "{{dataset.0.data.date}}"

  document.getElementById("datehead").innerHTML = "Bank Book Statement Of Month " + str1.substring(0,3) + str1.slice(7)


}

myFunction()

$('.showUpdateItem').click(function(){
  $('.update').css('display','none')
  $('#messageBox').css('display','none')
  $('#'+$(this).attr('item-id')).css('display','table-row')

})
