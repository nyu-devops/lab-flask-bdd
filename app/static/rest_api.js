$(function () {

    // ****************************************
    // Create a Pet
    // ****************************************

    $("#create-btn").click(function () {

        var name = $(this).parent().find("#create_name").val();
        var category = $(this).parent().find("#create_category").val();
        var available = $(this).parent().find("#create_available").val();

        var data = {
            "name": name,
            "category": category,
            "available": true
        };

        var ajax = $.ajax({
            type: "POST",
            url: "/pets",
            contentType:"application/json",
            data: JSON.stringify(data),
        });
        ajax.done(function(res){
            var result_id = res.id;
            var result_name = res.name;
            var result_category = res.category;
            var result_available = res.available;

            $("#create_result_id").empty();
            $("#create_result_name").empty();
            $("#create_result_category").empty();
            $("#create_result_available").empty();

            $("#create_result_id").append(result_id);
            $("#create_result_name").append(result_name);
            $("#create_result_category").append(result_category);
            $("#create_result_available").append(result_available);

            $("#flash_message").empty();
            $("#flash_message").append("Success");

        });
        ajax.fail(function(res){

            $("#create_result_id").empty();
            $("#create_result_name").empty();
            $("#create_result_category").empty();
            $("#create_result_available").empty();

            $("#flash_message").empty();
            $("#flash_message").append("Server error!");
        });

    });


    // ****************************************
    // Update a Pet
    // ****************************************

    $("#update-btn").click(function () {

        var pet_id = $(this).parent().find("#update_id").val();
        var name = $(this).parent().find("#update_name").val();
        var category = $(this).parent().find("#update_category").val();
        var available = $(this).parent().find("#update_available").val();

        var data = {
            "name": name,
            "category": category,
            "available": true
        };

        var ajax = $.ajax({
                type: "PUT",
                url: "/pets/" + pet_id,
                contentType:"application/json",
                data: JSON.stringify(data)
            })

        ajax.done(function(res){
            var result_id = res.id;
            var result_name = res.name;
            var result_category = res.category;
            var result_available = res.available;

            $("#update_result_id").empty();
            $("#update_result_name").empty();
            $("#update_result_category").empty();
            $("#update_result_available").empty();

            $("#update_result_id").append(result_id);
            $("#update_result_name").append(result_name);
            $("#update_result_category").append(result_category);
            $("#update_result_available").append(result_available);

            $("#flash_message").empty();
            $("#flash_message").append("Success");

        });
        ajax.fail(function(res){

            $("#update_result_id").empty();
            $("#update_result_name").empty();
            $("#update_result_category").empty();
            $("#update_result_available").empty();

            $("#flash_message").empty();
            $("#flash_message").append("Pet does not exist");

        });
    });

    // ****************************************
    // Retrieve a Pet
    // ****************************************

    $("#retrieve-btn").click(function () {

        var pet_id = $("#retrieve_id").val();

        var ajax = $.ajax({
            type: "GET",
            url: "/pets/" + pet_id,
            contentType:"application/json",
            data: ''
        })
        ajax.done(function(res){
            var result_id = res.id;
            var result_name = res.name;
            var result_category = res.category;
            var result_available = res.available;

            $("#retrieve_result_id").empty();
            $("#retrieve_result_name").empty();
            $("#retrieve_result_category").empty();
            $("#retrieve_result_available").empty();

            $("#retrieve_result_id").append(result_id);
            $("#retrieve_result_name").append(result_name);
            $("#retrieve_result_category").append(result_category);
            $("#retrieve_result_available").append(result_available);

            $("#flash_message").empty();
            $("#flash_message").append("Success");
        });
        ajax.fail(function(res){

            $("#retrieve_result_id").empty();
            $("#retrieve_result_name").empty();
            $("#retrieve_result_category").empty();
            $("#retrieve_result_available").empty();

            $("#flash_message").empty();
            $("#flash_message").append("Pet does not exist");

        });
    });

    // ****************************************
    // Delete a Pet
    // ****************************************

    $("#delete-btn").click(function () {

        var pet_id = $("#delete_id").val();

        var ajax = $.ajax({
            type: "DELETE",
            url: "/pets/" + pet_id,
            contentType:"application/json",
            data: '',
        })

        ajax.done(function(res){

            $("#delete_result").empty();
            $("#delete_result").append("Deleted!");

            $("#flash_message").empty();
            $("#flash_message").append("Success");
        });
        ajax.fail(function(res){

            $("#delete_result").empty();
            $("#delete_result").append("server error!");

        });
    });


})
