$(function(){
  $.get('/graph', function(result) {
    var style = [
      // 'background-color'和Bordercolor设为一样吧。。
      { selector: 'node[label="Movie"]',
        css: {'background-color': '#6FB1FC','border-color': '#6FB1FC','content': 'data(name)','border-width': 20}},
      { selector: 'node[label="Genre"]',
        css: {'background-color': '#F5A45D','border-color': '#F5A45D', 'content': 'data(name)','border-width': 20}},
      { selector: 'node[label="Person"]',
        css: {'background-color': 'red','border-color': 'red', 'content': 'data(name)','border-width': 20}},
      { selector: 'edge',
        css: {'target-arrow-shape': 'triangle','width':1,'line-color': 'grey','target-arrow-color': 'grey',}}
    ];

    var cy = cytoscape({
      container: document.getElementById('cy'),
      style: style,
      layout: { name: 'cose', fit: false },
      elements: result.elements
    });


var i = 0;
cy.unbind("tapdrag");
cy.unbind("tapend");

cy.bind("tapdrag", "node", function(evt){
    if (i = 0) {
        i = 1;
        var node = evt.target;
        var target = cy.edges("[source = '" + node.id() + "']").target();
        cy.automove({
             nodesMatching: target,
             reposition: 'drag',
             dragWith: node
        });
    }
});

cy.bind("tapend", "node", function(evt) {
    i = 0;
});
  }, 'json');


});