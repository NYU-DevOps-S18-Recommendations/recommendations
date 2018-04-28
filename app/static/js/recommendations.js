$(function () {

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    // Updates the form with data from the response
    function update_form_data(res) {
        $("#recommendation_id").val(res.id);
        $("#rec_product_id").val(res.recommended_product_id);
        $("#recommendation_type").val(res.recommendation_type);
        $("#likes").val(res.likes);
        if (res.available == true) {
            $("#rec_available").val("true");
        } else {
            $("#rec_available").val("false");
        }
    }

    /// Clears all form fields
    function clear_form_data() {
        $("#recommendation_id").val("");
        $("#recommendation_product_id").val("");
        $("#recommendation_type").val("");
        $("#likes").val("");
    }

    // Updates the flash message area
    function flash_message(message) {
        $("#flash_message").empty();
        $("#flash_message").append(message);
    }

    // ****************************************
    // Create a Recommendation
    // ****************************************

    $("#create-btn").click(function () {

        var recommendation_id = $("#recommendation_id").val();
        var recomendation_product_id = $("#recommendation_product_id").val();
        var recommendation_type = $("#recommendation_type").val();
        //var recommendation_likes = $("#likes").val();

        var data = {
            "recommendation_id": parseInt(recommendation_id),
            "recomendation_product_id": parseInt(recommendation_product_id),
            "recommendation_type": recommendation_type
            //"recommendation_likes": parseInt(likes)
        };

        var ajax = $.ajax({
            type: "POST",
            url: "/recommendations",
            contentType:"application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });
    });


    // ****************************************
    // Update a Recommendation
    // ****************************************

    $("#update-btn").click(function () {

        var recommendation_id = $("#recommendation_id").val();
        var recomendation_product_id = $("#recommendation_product_id").val();
        var recommendation_type = $("#recommendation_type").val();
        var recommendation_likes = $("#likes").val();

        var data = {
            "recommendation_id": parseInt(recommendation_id),
            "recomendation_product_id": parseInt(recomendation_product_id),
            "recommendation_type": recommendation_type
            "recommendation_likes": parseInt(likes)
        };

        var ajax = $.ajax({
                type: "PUT",
                url: "/recommendations/" + recommendation_id,
                contentType:"application/json",
                data: JSON.stringify(data)
            })

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Retrieve a Recommendation
    // ****************************************

    $("#retrieve-btn").click(function () {

        var recommendation_id = $("#recommendation_id").val();

        var ajax = $.ajax({
            type: "GET",
            url: "/recommendations/" + recommendation_id,
            contentType:"application/json",
            data: ''
        })

        ajax.done(function(res){
            //alert(res.toSource())
            update_form_data(res)
            flash_message("Success. Recommendation retrieved: " + recommendation_id)
        });

        ajax.fail(function(res){
            clear_form_data()
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Delete a Pet
    // ****************************************

    $("#delete-btn").click(function () {

        var recommendation_id = $("#recommendation_id").val();

        var ajax = $.ajax({
            type: "DELETE",
            url: "/recommendations/" + recommendation_id,
            contentType:"application/json",
            data: '',
        })

        ajax.done(function(res){
            clear_form_data()
            flash_message("Recommendation with ID [" + res.id + "] has been Deleted!")
            //or should it be recommendation_id
        });

        ajax.fail(function(res){
            flash_message("Server error!")
        });
    });

    // ****************************************
    // Clear the form
    // ****************************************

    $("#clear-btn").click(function () {
        $("#recommendation_id").val("");
        clear_form_data()
    });

    // ****************************************
    // Search for a Recommendation
    // ****************************************

    $("#search-btn").click(function () {

        var recommendation_id = $("#recommendation_id").val();
        var recomendation_product_id = $("#recommendation_product_id").val();
        var recommendation_type = $("#recommendation_type").val();
        var recommendation_likes = $("#likes").val();

        var queryString = ""

        if (recommendation_type) {
            queryString += 'recommendation_type=' + recommendation_type
        }

        if (recommendation_id) {
            if (queryString.length > 0) {
                queryString += '&recommendation_id=' + recommendation_id
            } else {
                queryString += 'recommendation_id=' + recommendation_id
            }
        }

        if (recommendation_product_id) {
            if (queryString.length > 0) {
                queryString += '&recommendation_product_id=' + recommendation_product_id
            } else {
                queryString += 'recommendation_product_id=' + recommendation_product_id
            }
        }

        if (recommendation_likes) {
            if (queryString.length > 0) {
                queryString += '&recommendation_likes=' + recommendation_likes
            } else {
                queryString += 'recommendation_likes=' + recommendation_likes
            }
        }

        var ajax = $.ajax({
            type: "GET",
            url: "/recommendations?" + queryString,
            contentType:"application/json",
            data: ''
        })

        ajax.done(function(res){
            //alert(res.toSource())
            $("#search_results").empty();
            $("#search_results").append('<table class="table-striped">');
            var header = '<tr>'
            header += '<th style="width:10%">Recommendation_ID</th>'
            header += '<th style="width:40%">Recommendation_Product_ID</th>'
            header += '<th style="width:40%">Recommendation_Type</th>'
            header += '<th style="width:10%">Recommendation_Likes</th></tr>'
            $("#search_results").append(header);
            for(var i = 0; i < res.length; i++) {
                recommendation = res[i];
                var row = "<tr><td>"+recommendation.id+"</td><td>"+recommendation.recommended_product_id+"</td><td>"+recommendation.recommendation_type+"</td><td>"+recommendation.likes+"</td></tr>";
                $("#search_results").append(row);
            }

            $("#search_results").append('</table>');

            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });


    // ****************************************
    // Like a Recommendation
    // ****************************************

    $("#like-btn").click(function () {

        var recommendation_id = $("#recommendation_id").val();
        // var recomendation_product_id = $("#recommendation_product_id").val();
        // var recommendation_type = $("#recommendation_type").val();
        // var recommendation_likes = $("#likes").val();

        var data = {
            "recommendation_id": parseInt(recommendation_id),
            // "recomendation_product_id": parseInt(recommendation_product_id),
            // "recommendation_type": recommendation_type
            // /"recommendation_likes": parseInt(likes)
        };


        var ajax = $.ajax({
                type: "PUT",
                url: "/recommendations/" + recommendation_id + '/likes',
                contentType:"application/json",
                data: JSON.stringify(data)
            })

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });
    });


})