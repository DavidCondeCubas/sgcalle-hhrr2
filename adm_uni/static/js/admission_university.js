"use strict"
var studentCount = 1;

function removeStudent(idStudent){
    studentCount--;
    $(`#navStudent${idStudent}`).remove();
    $(`#student${idStudent}`).remove();
}

function addStudent(){
    studentCount++;
    var htmlTab =
`<li class="nav-item" style="position: relative" id="navStudent${studentCount}">
    <a class="nav-link" id="student${studentCount}-tab" data-toggle="tab" href="#student${studentCount}"
       role="tab" aria-controls="student${studentCount}" aria-selected="false">Student ${studentCount}</a>
       <i class="fa fa-times" style="position: absolute; top: -0.5em; right: 0.1em; font-size: 1.4em; color: orangered; cursor: pointer;"
          onclick="removeStudent(${studentCount})"></i>
</li>`;


    $(htmlTab).insertBefore($(this).parent());

    $('#studentsCount').val(studentCount);

    var studentClonnable  = document.getElementById("student1").cloneNode(true);
    var studentTabContent = document.getElementById("studentsTabContent");
    
    studentTabContent.appendChild(studentClonnable);
    
    // Reassign ids
    $(studentClonnable).attr("id", "student"+studentCount);
    $(studentClonnable).attr("aria-labelledby", "student"+studentCount+"-tab");
    $(studentClonnable).removeClass("active");
    $(studentClonnable).removeClass("show");
    
    // Year List
    var optionsSchoolYear = $('select#selStudent1SchoolYear option').clone();
    $('#selStudent'+studentCount+'SchoolYear').append(optionsSchoolYear);

    // Grade Level List
    var optionsGradeLevel = $('select#selStudent1GradeLevel option').clone();
    $('#selStudent'+studentCount+'GradeLevel').append(optionsGradeLevel);
}

function addContact(){
	$(this).find("i").removeClass("fa-plus").addClass("fa-minus");
	$(this).removeClass("btn-primary").addClass("btn-danger");
	
	$(this).removeClass("add_contact");
	
	$(this).off("click");
	$(this).on("click", removeContact);
	
	// Create new contact
	var contactHtml =
	'<div class="row mt-3">'+
	'    <div class="col-5">'+
	'        <input class="form-control" name="txtContactName"'+
	'            placeholder="Skype, Whatsapp..." />'+
	'    </div>'+
	'    <div class="col-5">'+
	'        <input class="form-control" name="txtContactId"'+
	'            placeholder="phone, email, username..." />'+
	'    </div>'+
	'    <div class="col-2">'+
	'        <button type="button" class="w-100 btn btn-primary add_contact">'+
	'            <i class="fa fa-plus"></i>'+
	'        </button>'+
	'    </div>'+
	'</div>';
	$('#contacts').append(contactHtml);
	$(".add_contact").on("click", addContact);
	
}

function removeContact(){
	$(this).parent().parent().remove();
}

function addLanguage(){
	
	$(this).find("i").removeClass("fa-plus").addClass("fa-minus");
	$(this).removeClass("btn-primary").addClass("btn-danger");
	
	$(this).removeClass("add_langage");
	
	$(this).off("click");
	$(this).on("click", removeContact);
	
	var langaugeRow = 
	'<div class="col-5">'+
	'    <select class="form-control selectLanguage" name="selLanguage">'+
	'    </select>'+
	'</div>'+
	'<div class="col-5">'+
	'    <select class="form-control selectLanguageLevel" name="selLanguageLevel">'+
	'    </select>'+
	'</div>'+
	'<div class="col-2">'+
	'    <button type="button" class="w-100 btn btn-primary add_language">'+
	'        <i class="fa fa-plus"></i>'+
	'    </button>'+
	'</div>';
	
	var $languageRow = $("<div class='row mt-3'></div>");
	
	$languageRow.html(langaugeRow);

	$languageRow.find(".selectLanguage").html($("#selLanguage").html());
	$languageRow.find(".selectLanguageLevel").html($("#selLanguageLevel").html());
	
	$('#languages').append($languageRow);
	$languageRow.on("click", ".add_language", addLanguage);
}

function getStates(){
    $('#selState').html("<option value='-1'>-Select a state-</option>");
    $.ajax({
        url: '/admission/states',
        type: 'GET',
        data: { 'country_id': $('#selCountry').val()},
        success: function(data){
            $.each(JSON.parse(data), function(i, state){
                // console.log(`<option
				// value='${state.id}'>${state.name}</option>`);
                $('#selState').append(`<option value='${state.id}'>${state.name}</option>`)
            })
        },
        error: function(){
            console.error("Un error ha ocurrido al cargar los states");
        }
    });

}

$(function(){
    $('#add-tab').on('click', addStudent);
    $('#selCountry').on('change', getStates);
    
    $('.custom-file-input').on("change", function(){
    	var fileName = $(this)[0].files[0].name;
    	$(this).next("label").text(fileName);
    });
    
    $(".add_contact").on("click", addContact);
    $(".add_language").on("click", addLanguage)
});
