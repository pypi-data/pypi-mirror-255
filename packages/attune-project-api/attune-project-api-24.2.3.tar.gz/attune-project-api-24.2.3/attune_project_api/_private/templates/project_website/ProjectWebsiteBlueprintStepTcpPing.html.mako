<%page args="step"/>

    <div class="row">
        <p class="mb-0">
% if step.preWait:
            Wait <strong>${step.preWait}</strong> seconds.
% endif
            Check if TCP Port <strong>${step.preWait}</strong> is listening.
% if step.minDowntime:
            Make sure the TCP Port goes down for
            <strong>${step.minDowntime}</strong> seconds.
% endif
% if step.postWait:
            When the TCP Port is up, wait <strong>${step.postWait}</strong>
            seconds.
% endif
        </p>
        <p>Use Telnet to check if the TCP Service is accepting connections.</p>
    </div>
