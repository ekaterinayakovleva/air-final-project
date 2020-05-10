import {Component, Input, OnInit} from '@angular/core';

@Component({
    selector: 'app-block',
    template: `
        <div class="ui-g-12">
            <hr style="margin-left:20px">
            <div class="ui-g-6 img-container">
                <img src="{{url}}" alt="" class="image">
            </div>
            <div class="ui-g-5">
                <span style="font-size: 20px">{{description}}</span>
            </div>
        </div>
    `,
    styleUrls: ['./block.component.css']
})
export class BlockComponent {
    @Input() description: string
    @Input() url: string
}
