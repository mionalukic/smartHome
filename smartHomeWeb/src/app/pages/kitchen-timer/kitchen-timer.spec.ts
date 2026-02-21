import { ComponentFixture, TestBed } from '@angular/core/testing';

import { KitchenTimer } from './kitchen-timer';

describe('KitchenTimer', () => {
  let component: KitchenTimer;
  let fixture: ComponentFixture<KitchenTimer>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [KitchenTimer]
    })
    .compileComponents();

    fixture = TestBed.createComponent(KitchenTimer);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
