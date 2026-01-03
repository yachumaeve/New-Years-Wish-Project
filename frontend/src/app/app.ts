import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DataService } from './service/data';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { WishItem } from './models/type';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './app.html',
  styleUrls: ['./app.css']
})
export class AppComponent implements OnInit {
  
  wishlList: WishItem[] = []; //募資項目清單
  selectedItem: WishItem | null = null; //所選募資項目
  donationForm: FormGroup; //捐贈者資料表單
  showSuccess = false; //資料是否送出成功
  isLoading = false; // 是否顯示Loader
  errorMsg: string = ''; //儲存錯誤訊息

  constructor(private dataService: DataService, private fb: FormBuilder) {
    this.donationForm = this.fb.group({
      name: ['', Validators.required],
      phone: ['', [Validators.required, Validators.pattern('^09[0-9]{8}$')]],
      email: ['', [Validators.required, Validators.email]]
    });
  }

  ngOnInit() {
    this.fetchRecipients();
  }

  /**
   * 取得機構募資項目
   */
  fetchRecipients(): void {
    this.isLoading = true;
    this.selectedItem = null;
    this.dataService.getRecipients().subscribe({
      next: (data: WishItem[]) => {
        this.wishlList = data;
        this.isLoading = false;
        console.log('募集項目更新成功');
        console.log(data);
      },
      error: (err) => {
        this.isLoading = false;
        console.error('API 連線失敗：', err);
        this.showError('目前無法取得物資清單，請稍後再試。');
      }
    });
  }

  /**
   * 處理姓名顯示 (Ex. 陳Ｏ華)
   * @param name 
   * @returns 
   */
  formatName(name: string): string {
    if (name.length <= 1) return name;
    if (name.length === 2) return name[0] + 'Ｏ';
    return name[0] + 'Ｏ' + name[name.length - 1];
  }

  /**
   * 開啟資料填寫popup
   * @param item 
   */
  openModal(item: WishItem) {
    if (item.is_taken_on === 0) {
      this.selectedItem = item;
      this.showSuccess = false;
      this.donationForm.reset();
    }
  }

  /**
   * 關閉資料填寫popup
   */
  closeModal() {
    this.selectedItem = null;
  }

  /**
   * 送出資料填寫表單
   */
  submitDonation() {
    this.isLoading = true;
    if (this.donationForm.valid && this.selectedItem) {
      const donorData = {
        donor_name: this.donationForm.value.name,
        contact_phone: this.donationForm.value.phone,
        email: this.donationForm.value.email,
        recipient_id: this.selectedItem.recipient_id
      };
  
      this.dataService.submitDonation(donorData).subscribe({
        next: (res) => {
          this.isLoading = false;
          this.showSuccess = true;
          this.fetchRecipients();
        },
        error: (err) => {
          this.isLoading = false;
          console.error('送出失敗', err);
          this.showError('認領失敗，該項目可能剛被他人認領，請重試。');
        }
      });
    }
  }

  private showError(msg: string) {
    this.errorMsg = msg;
    setTimeout(() => {
      this.errorMsg = '';
    }, 3000); // 3秒後自動清除
  }
  
}