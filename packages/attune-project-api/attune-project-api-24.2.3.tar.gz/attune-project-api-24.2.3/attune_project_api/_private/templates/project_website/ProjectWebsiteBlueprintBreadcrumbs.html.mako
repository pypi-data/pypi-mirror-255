<%page args="projectMetadata, blueprint"/>
<!-- Project breadcrumbs -->
<div class="container px-0">
    <div class="row">
        <nav class="col px-0" aria-label="breadcrumb">
            <ol class="breadcrumb">
                <li class="breadcrumb-item">
                    <a href="index.html">
                    <strong>Attune Project: </strong>${projectMetadata.name}
                    </a>
                </li>
                <li class="breadcrumb-item active" aria-current="page">
                    <strong>${blueprint.name}</strong>
                </li>
            </ol>
        </nav>
    </div>
</div>