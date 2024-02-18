<%page args="blueprints"/>
            <div class="col-lg-10 mt-3 px-0">
                <div class="container">
                    <div class="row">
                        <div class="col pl-0">
                            <p>
                                This project contains the following
                                documentation and instruction sets:
                            </p>
                        </div>
                    </div>

                    <!-- Blueprints listed with names and descriptions -->
                    <div class="row">
% for blueprint in blueprints:
<%
    blueprintName = blueprint.name.replace(" ", "-").replace(".", "-")
%>
                        <div class="col-12 pt-3 pl-0">
                            <div class="card"
                                 id="${blueprintName}">
                                <div class="card-body">
                                    <a href="${blueprintName}.html">
                                        <h3 class="card-title">
                                            ${blueprint.name}
                                        </h3>
                                    </a>
% if blueprint.comment:
                                    <div class="description">
                                        <p class="card-text">
                                            ${blueprint.makeCommentHtml(4)}
                                        </p>
                                    </div>
% endif
                                </div>
                            </div>
                        </div>
% endfor
                    </div>
                </div>
            </div>