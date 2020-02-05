'use strict';
/**
 For dataset section
 **/


/**
 JS Code for Listing
 **/

const removeDataset = (id) => {
    if (id === "") {
        return
    }
    $.ajax({
        url: "/dataset/datasets",
        method: "POST",
        data: {
            id: id,
            action: 'DELETE'
        },
    }).done(function (data) {
        table.remove('id', data.id);
    });
};

$("#dataset-table").click(e => {
    if (!e.target) {
        return;
    }
    const classes = $(e.target).attr("class");
    if (classes.includes("btn-danger")) {
        removeDataset($(e.target).data("id"))
    } else if (classes.includes("fa-times")) {
        removeDataset($(e.target).parent().data("id"))
    }
});
