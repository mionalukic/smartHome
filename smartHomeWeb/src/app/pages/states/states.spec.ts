import { ComponentFixture, TestBed } from '@angular/core/testing';

import { States } from './states';

describe('States', () => {
  let component: States;
  let fixture: ComponentFixture<States>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [States]
    })
    .compileComponents();

    fixture = TestBed.createComponent(States);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
