class RestAPI {
  constructor({logger}) {
    this.csrftoken = this.getCookie('csrftoken');
    this.logger = logger
  }

  getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
  }

  write(packet) {
    $.ajax({
      type: "PUT",
      url: "/api/v1/dcc/command",
      data: packet,
      success: function (data) { displayLog('[RECEIVE] '+data.response.replace(/\n/g,"")); },
      contentType: "text/plain",
      headers: {'X-CSRFToken': this.csrftoken}
    });
  }
}
