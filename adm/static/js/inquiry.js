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
    
    $(studentClonnable).find("input").each(function() {
    	$(this).val("");
    });
    
    
    // Year List
    var optionsSchoolYear = $('select#selStudent1SchoolYear option').clone();
    $('#selStudent'+studentCount+'SchoolYear').append(optionsSchoolYear);

    // Grade Level List
    var optionsGradeLevel = $('select#selStudent1GradeLevel option').clone();
    $('#selStudent'+studentCount+'GradeLevel').append(optionsGradeLevel);
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

function changeState() {
	var select_state = $('#selState')
	select_state.children("option:gt(0)").hide();
	select_state.children("option[data-country='" + $(this).val() + "']").show();

	if (select_state.children("option:selected").is(":hidden")){
		select_state.children("option:nth(0)").prop("selected", true);
	}
}

function ready(fn) {
    if (document.readyState != 'loading'){
        fn();
    } else {
        document.addEventListener('DOMContentLoaded', fn);
    }
}

ready(function(){

    document.querySelector("#add-tab").addEventListener("click", addStudent)
    document.querySelector("#selCountry").addEventListener("change", changeState)

    document.querySelectorAll(".custom-file-input").forEach(function(element){
        element.addEventListener("change", function(){
            var fileName = this.files[0].name
            $(this).next("label").text(fileName);
        })
    })
});
