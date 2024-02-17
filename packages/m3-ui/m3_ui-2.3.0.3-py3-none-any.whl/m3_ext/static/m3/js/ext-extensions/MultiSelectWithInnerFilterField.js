Ext.ns('Ext.m3');

/**
 * @class Ext.ux.form.MultiSelectWithInnerFilterField
 * @extends Ext.m3.MultiSelectField
 *
 * Контрол для выбора множества значений с внутренним фильтром записей
 */
Ext.m3.MultiSelectWithInnerFilterField = Ext.extend(Ext.m3.MultiSelectField, {

    /**
     * Id опции Выделить все
     */
    optAllId: -5,
    optAllLabel: '(Выделить все)',

    /**
     * Предыдущие сохранённые записи
     */
    prevCheckedItems: [],

    /**
     * Отмеченные записи внутреннего фильтра выпадающего списка
     */
    filterCheckedItems: [],

    /**
     * Id записи внутреннего фильтра выпадающего списка ('Добавить выделенный фрагмент в фильтр')
     */
    filterApplyId: -1,
    optFilterApplyLabel: 'Добавить выделенный фрагмент в фильтр',
    optFilterAllLabel: '(Выделить все результаты поиска)',

    /**
     * Ширина иконки чекбокса
     */
    checkboxImageWidth: 16,

    /**
     * Минимальная ширина выпадающего списка
     */
    dropDownListMinWidth: 155,

    /**
     * Режим фильтрации
     */
    filterMode: false,

    resizable: true,

    innerListWidthConst: 9,
    filterFieldDivWidthConst: 17,
    /**
     * Метод расширен для добавления функционала Выделить все записи/Снять выделение всех записей
     */
    initComponent:function() {
        this.checkedItems = [];

        if (!this.tpl) {
             this.tpl = '<tpl for=".">' +
             '<div ext:qtip="{' + this.displayField + '}" style="width: max-content;" class="x-combo-list-item x-multi-combo-item">' +
            '<img src="' + Ext.BLANK_IMAGE_URL + '" class="{[this.getImgClass(values)]}" />' +
            '<div style="padding-right:' + this.checkboxImageWidth + 'px">{' + this.displayField + '}</div></div></tpl>';

            this.tpl = new Ext.XTemplate(this.tpl, {
                getImgClass: this.getCheckboxCls.createDelegate(this)
            })
        }

        var data = this.store.reader.readRecords([
            [this.optAllId, this.optAllLabel]
        ]);
        this.store.insert(0, data.records);

        for (var i = 0; i < this.store.data.items.length; i++) {
            var record = this.store.data.items[i];
            this.checkedItems.push(record);
            this.prevCheckedItems.push(record);
        }

        Ext.m3.MultiSelectField.superclass.initComponent.apply(this);
    },
    findCheckedRecord:function(record, checkedItems) {
        var index = -1;

        for (var i = 0; i < checkedItems.length; i++) {
            if (checkedItems[i].data[this.valueField] === record.data[this.valueField]) {
                index = i;
                break;
            }
        }

        return index;
    },
    onTriggerDropDownClick: function () {
        if (this.fireEvent('beforerequest', this)) {

            if (this.isExpanded()) {
                this.restorePreviousItems();
                this.collapse();
            } else {
                this.onFocus({});
                this.doQuery(this.allQuery, true);
            }
            this.el.focus();
        }
    },
    collapse : function(){
        if(!this.isExpanded()){
            return;
        }
        this.list.hide();
        this.fireEvent('collapse', this);
    },
    /**
     * Обработчик кнопки ОК внутри выпадающего списка
     */
    okBtnHandler: function() {
        if (!this.filterOkBtn.disabled) {
            if (this.filterMode) {
                this.checkedItems.splice(0, this.checkedItems.length);
                for (var i = 0; i < this.filterCheckedItems.length; i++) {
                    var filteredRecord = this.filterCheckedItems[i];
                    if (filteredRecord.data.id !== this.optAllId) {
                        this.checkedItems.push(filteredRecord);
                    }
                }

                this.filterMode = false;
                this.tpl.filterMode = false;
                this.filterField.dom.value = '';
                this.toggleFilterFieldSpanIcon(true);
                this.view.refresh();
            }

            this.columnSpanTrigger = new Ext.Element(this.ownerCt.el.select('span').elements[0]);

            new Ext.ToolTip({
                width: 160,
                target: this.columnSpanTrigger,
                title: 'Результаты отфильтрованы',
                mouseOffset: [-170, 0]
            });

            this.prevCheckedItems = [];
            for (var i = 0; i < this.checkedItems.length; i++) {
                this.prevCheckedItems.push(this.checkedItems[i]);
            }

            // Меняется иконка триггера колоночного фильтра
            var columnSpanTriggerId = this.wrap.select('img').elements[1].id;
            Ext.get(columnSpanTriggerId).addClass('x-form-filter-trigger');

            this.collapse();

            this.fireEvent("select", this, this.checkedItems);
        }
    },
    /**
     * Обработчик кнопки ЗАКРЫТЬ внутри выпадающего списка
     */
    closeBtnHandler: function() {
        this.restorePreviousItems();
        this.collapse();
    },
    /**
     * Меняет иконку поля фильтрации
     * @param {boolean} flag
     */
    toggleFilterFieldSpanIcon: function(flag) {
        if (flag) {
            this.filterFieldTrigger.dom.childNodes[0].style.display = '';
            this.filterFieldTrigger.dom.childNodes[1].style.display = 'none';
        } else {
            this.filterFieldTrigger.dom.childNodes[0].style.display = 'none';
            this.filterFieldTrigger.dom.childNodes[1].style.display = '';
        }
    },
    /**
     * Восстанавливает предыдущие значения колоночного фильтра
     */
    restorePreviousItems: function() {
        this.filterField.dom.value = '';
        this.toggleFilterFieldSpanIcon(true);

        this.filterMode = false;
        this.tpl.filterMode = false;

        this.checkedItems.splice(0, this.checkedItems.length);
        this.view.refresh();

        for (var i = 0; i < this.prevCheckedItems.length; i++) {
            var record = this.prevCheckedItems[i];
            this.checkedItems.push(record);
            this.refreshItem(record);
        }
    },
    /**
     * Копирует метод collapseIf, но добавляет восстановление к предыдущим значениям колоночного фильтра
     */
    closeIf: function(e){
        if(!this.isDestroyed && !e.within(this.wrap) && !e.within(this.list)){
            this.restorePreviousItems();
            this.collapse();
        }
    },
    expand : function(){
        this.activateFilterOkBtn();

        if(this.isExpanded() || !this.hasFocus){
            return;
        }

        if(this.title || this.pageSize){
            this.assetHeight = 0;
            if(this.title){
                this.assetHeight += this.header.getHeight();
            }
            if(this.pageSize){
                this.assetHeight += this.footer.getHeight();
            }
        }

        var width = this.bufferSize >= this.dropDownListMinWidth ? this.bufferSize : this.dropDownListMinWidth;
        this.doResize(width);
        this.list.alignTo.apply(this.list, [this.el].concat(this.listAlign));


        this.list.setZIndex(this.getZIndex());
        this.list.show();
        if(Ext.isGecko2){
            this.innerList.setOverflow('auto');
        }

        this.mon(Ext.getDoc(), {
            scope: this,
            mousewheel: this.closeIf,
            mousedown: this.closeIf
        });

        this.fireEvent('expand', this);
    },
    restrictHeight : function(){
        this.innerList.dom.style.height = '';

        this.list.beginUpdate();
        this.list.setHeight(380);
        this.list.alignTo.apply(this.list, [this.el].concat(this.listAlign));
        this.list.endUpdate();

        this.innerList.setHeight(this.list.getHeight() - this.filterFieldWrapDiv.getHeight() - 39);
        this.outerDiv.setHeight(this.list.getHeight());
    },
    selectByValue : function(v, scrollIntoView){
        if(!Ext.isEmpty(v, true)){
            var r = this.findRecord(this.valueField || this.displayField, v);
            if(r){
                this.select(this.store.indexOf(r), scrollIntoView);
                return true;
            }
        }
        return false;
    },
    getCheckboxCls : function(record) {
        var checkedItems = this.tpl.filterMode ? this.filterCheckedItems : this.checkedItems;

        for (var i = 0; i < checkedItems.length; i++) {
            if (record[this.valueField] == checkedItems[i].data[this.valueField]) {
                return 'x-grid3-check-col-on';
            }
        }

        return 'x-grid3-check-col';
    },
    onViewClick : function(doFocus){
        var index = this.view.getSelectedIndexes()[0],
            s = this.filterMode ? this.filterStore : this.store,
            r = s.getAt(index);

        if(r){
            this.onSelect(r, index);
        }else {
            this.collapse();
        }
        if(doFocus !== false){
            this.el.focus();
        }
    },
    /**
     * Подгатавливает store записей для режима фильтрации
     * @param {string} value Строка в поле фильтрации
     */
    prepareFilterStoreData: function(value) {
        var childNodesLength = this.innerList.dom.childNodes.length,
            records = [
                {data: {id: this.optAllId, name: this.optFilterAllLabel}},
                {data: {id: this.filterApplyId, name: this.optFilterApplyLabel}}
            ],
            filterStoreData = [];

        for (var i = 0; i < childNodesLength; i++) {
            this.innerList.dom.lastChild.remove();
        }

        for (var i = 0; i < records.length; i++) {
            var r = records[i];
            filterStoreData.push([r.data.id, r.data.name]);
        }

        for (var i = 0; i < this.store.data.items.length; i++) {
            var r = this.store.data.items[i];
            if (r.data.id !== this.optAllId && r.data.name.toLocaleLowerCase().includes(value)) {
                records.push(r);
                filterStoreData.push([r.data.id, r.data.name]);
            }
        }

        this.filterStore = new Ext.data.Store({
            listeners: {},
            reader: new Ext.data.ArrayReader(
                {idIndex: 0},
                Ext.data.Record.create([
                    {name: "id", mapping: 0},
                    {name: "name", mapping: 1}
                ])
            ),
            data: filterStoreData
        });

        for (var i = 0; i < records.length; i++) {
            var r = records[i];
            if (r.data.id !== this.filterApplyId) {
                this.filterCheckedItems.push(r);
            }
        }

        return records;
    },
    /**
     * Обработчик события KeyUp поля фильтрации
     * @param {Ext.EventObjectImpl} event
     */
    filterFieldOnKeyUp : function(event) {
        var value = event.target.value.toLocaleLowerCase(),
            el = this.view.getTemplateTarget(),
            records = [];

        if (value.length === 0) {
            if (this.checkedItems.length === 0) {
                this.disableFilterOkBtn();
            }
            records = this.store.getRange();
            this.filterMode = false;
            this.tpl.filterMode = false;
            this.toggleFilterFieldSpanIcon(true);
        } else if (value.length === 1) {
            this.activateFilterOkBtn();
            this.toggleFilterFieldSpanIcon(false);
            return;
        } else {
            this.filterCheckedItems.splice(0, this.filterCheckedItems.length);
            this.filterMode = true;
            this.tpl.filterMode = true;
            this.toggleFilterFieldSpanIcon(false);
            records = this.prepareFilterStoreData(value);
        }

        this.view.tpl.overwrite(this.innerList, this.view.collectData(records, 0));
        this.view.all.fill(Ext.query(this.view.itemSelector, el.dom));
        this.view.updateIndexes(0);
    },
    /**
     * Обработчик триггера очищения поля фильтрации
     */
    onClearFilterTriggerClick : function() {
        if (this.checkedItems.length === 0) {
            this.disableFilterOkBtn();
        }

        var records = this.store.getRange(),
            el = this.view.getTemplateTarget();

        this.filterMode = false;
        this.tpl.filterMode = false;

        this.view.tpl.overwrite(this.innerList, this.view.collectData(records, 0));
        this.view.all.fill(Ext.query(this.view.itemSelector, el.dom));
        this.view.updateIndexes(0);

        this.filterField.dom.value = '';
        this.toggleFilterFieldSpanIcon(true);
    },
    onResize : function(w, h){
        Ext.form.ComboBox.superclass.onResize.apply(this, arguments);
        this.bufferSize = w;
    },
    doResize: function(w){
        var lw = Math.max(w, this.minListWidth);
        this.list.setWidth(lw);
        this.innerList.setWidth(lw - this.list.getFrameWidth('lr') - this.innerListWidthConst);
        this.filterField.setWidth(this.filterFieldWrapDiv.getWidth() - this.filterFieldDivWidthConst);
    },
    /**
     * Создаёт кнопки
     */
    initButtons: function() {
        this.buttonsDiv = this.outerDiv.createChild({
            style: 'float: right; margin-top: 3px; margin-right: 3px;'
        });

        this.filterOkBtn = new Ext.Button({
            text: 'ОК',
            enableToggle: false,
            allowDepress: false,
            pressed: false,
            renderTo: this.buttonsDiv.id,
            style: {
                display: 'inline',
                marginRight: '5px'
            }
        });
        this.filterOkBtn.getEl().select('button').elements[0].style.width = '50px';
        this.filterOkBtn.getEl().on('click', this.okBtnHandler, this);

        this.filterCloseBtn = new Ext.Button({
            text: 'Закрыть',
            enableToggle: false,
            allowDepress: false,
            pressed: false,
            renderTo: this.buttonsDiv.id,
            style: {display: 'inline'}
        });
        this.filterCloseBtn.getEl().select('button').elements[0].style.width = '70px';
        this.filterCloseBtn.getEl().on('click', this.closeBtnHandler, this);
    },
    /**
     * Создаёт поле фильтрации
     */
    initFilterField: function() {
        this.filterField = this.outerDiv.createChild({
            tag: 'input',
            type: 'text',
            size: 24,
            autocomplete: 'off',
            cls: 'x-form-text x-form-field',
            placeholder: 'Поиск'
        });

        this.filterFieldWrapDiv = this.filterField.wrap({
            cls: 'x-form-field-wrap x-form-field-trigger-wrap',
            style: 'margin-bottom: 5px;'
        });

        var triggerConfig = {
            tag: 'span',
            cls: 'x-form-twin-triggers',
            cn: [
                {tag: 'img', cls: 'x-form-trigger x-form-search-trigger', src: Ext.BLANK_IMAGE_URL},
                {tag: 'img', cls: 'x-form-trigger x-form-clear-trigger', src: Ext.BLANK_IMAGE_URL}
            ]
        };

        this.filterFieldTrigger = this.filterFieldWrapDiv.createChild(triggerConfig);
        var clearFilterTrigger = this.filterFieldTrigger.dom.childNodes[1];
        clearFilterTrigger.style.display = 'none';

        var clearFilterTriggerEl = new Ext.Element(clearFilterTrigger);
        this.mon(clearFilterTriggerEl, 'click', this.onClearFilterTriggerClick, this, {preventDefault:true});

        this.filterField.on('keyup', this.filterFieldOnKeyUp, this);
    },
    initList : function(){
        if(!this.list){
            var cls = 'x-combo-list',
                listParent = Ext.getDom(this.getListParent() || Ext.getBody());

            this.list = new Ext.Layer({
                parentEl: listParent,
                shadow: this.shadow,
                cls: [cls, this.listClass].join(' '),
                constrain: false,
                zindex: this.getZIndex(listParent)
            });

            var lw = this.listWidth || Math.max(this.wrap.getWidth(), this.minListWidth);
            this.list.setSize(lw, 0);
            this.list.swallowEvent('mousewheel');
            this.assetHeight = 0;
            if(this.syncFont !== false){
                this.list.setStyle('font-size', this.el.getStyle('font-size'));
            }
            if(this.title){
                this.header = this.list.createChild({cls: cls + '-hd', html: this.title});
                this.assetHeight += this.header.getHeight();
            }

            this.outerDiv = this.list.createChild({style: 'padding: 5px;'});

            this.initFilterField();

            this.innerList = this.outerDiv.createChild({cls: cls + '-inner'});
            this.innerList.dom.style.overflowX = 'scroll';
            this.innerList.dom.style.overflowY = 'scroll';

            this.mon(this.innerList, 'mouseover', this.onViewOver, this);
            this.mon(this.innerList, 'mousemove', this.onViewMove, this);

            this.initButtons();

            if(this.pageSize){
                this.footer = this.list.createChild({cls: cls + '-ft'});
                this.pageTb = new Ext.PagingToolbar({
                    store: this.store,
                    pageSize: this.pageSize,
                    renderTo:this.footer
                });
                this.assetHeight += this.footer.getHeight();
            }

            this.view = new Ext.DataView({
                applyTo: this.innerList,
                tpl: this.tpl,
                singleSelect: true,
                selectedClass: this.selectedClass,
                itemSelector: this.itemSelector || '.' + cls + '-item',
                emptyText: this.listEmptyText,
                deferEmptyText: false
            });

            this.mon(this.view, {
                containerclick : this.onViewClick,
                click : this.onViewClick,
                scope :this
            });

            this.bindStore(this.store, true);

            if(this.resizable){
                this.resizer = new Ext.Resizable(this.list,  {
                    handles: 'e',
                    minWidth: this.dropDownListMinWidth
                });
                this.mon(this.resizer, 'resize', function(r, w, h){
                    this.maxHeight = h - this.handleHeight - this.list.getFrameWidth('tb') - this.assetHeight;
                    this.listWidth = w;
                    this.innerList.setWidth(w - this.list.getFrameWidth('lr') - this.innerListWidthConst);
                    this.filterField.setWidth(this.filterFieldWrapDiv.getWidth() - this.filterFieldDivWidthConst);
                    this.restrictHeight();
                }, this);
            }
        }
    },
    onTriggerClick : function(event, el){
        // Чтобы нельзя было скрыть фильтр, нажав на поле ввода
        return false;
    },
    getText : function () {
        return '';
	},
    /**
     * Перенесён функционал из Ext.DataView.refreshNode, чтобы не создавать
     * кастомный клас наследник Ext.DataView
     * @param {integer} index
     * @param {Ext.data.Record} record
     */
    viewRefreshNode : function(index, record) {
        var view = this.view;

        if(index > -1) {
            var sel = view.isSelected(index),
                original = view.all.elements[index],
                node = view.bufferRender([record], index)[0];

            view.all.replaceElement(index, node, true);
            if(sel){
                view.selected.replaceElement(original, node);
                view.all.item(index).addClass(view.selectedClass);
            }
            view.updateIndexes(index, index);
        }
    },
    refreshItem : function(record) {
        var store = this.filterMode ? this.filterStore : this.store;

        if (this.view) {
            this.viewRefreshNode(store.indexOf(record), record);
        }
    },
    /**
     * Выбор записи в режиме фильтрации
     * @param {Ext.data.Record} record
     * @param {integer} checkedIndex
     * @param {Ext.data.Store} store
     * @param {object} checkedItems
     */
    filterSelect : function(record, checkedIndex, store, checkedItems) {
        if (record.data.id === this.optAllId) {
            var allChecked = this.findCheckedRecord(record, checkedItems) !== -1;

            for (var i = 0; i < store.data.items.length; i++) {
                var item = store.data.items[i],
                    index = this.findCheckedRecord(item, checkedItems);

                if(item.data.id !== this.filterApplyId) {
                    if (allChecked && index !== -1) {
                        checkedItems.remove(checkedItems[index]);
                    } else if (index === -1) {
                        checkedItems.push(item);
                    }
                    this.refreshItem(item);
                }
            }
        } else if (record.data.id === this.filterApplyId) {
            for (var i = 0; i < this.filterCheckedItems.length; i++) {
                var r = this.filterCheckedItems[i];

                if (r.data.id !== this.optAllId && this.checkedItems.indexOf(r) === -1) {
                    this.checkedItems.push(r);
                }
            }

            this.onClearFilterTriggerClick();
        } else {
            this.selectCommonRecord(record, checkedIndex, store, checkedItems);
        }
    },
    /**
     * Отключает кнопку ОК
     */
    disableFilterOkBtn : function() {
        this.filterOkBtn.disable();
    },
    /**
     * Активирует кнопку ОК
     */
    activateFilterOkBtn : function() {
        this.filterOkBtn.setDisabled(false);
    },
    /**
     * Выбор записи в режиме дефолтном режиме
     * @param {Ext.data.Record} record
     * @param {integer} checkedIndex
     * @param {Ext.data.Store} store
     * @param {object} checkedItems
     */
    defaultSelect : function(record, checkedIndex, store, checkedItems) {
        if (record.data.id === this.optAllId) {
            var allChecked = this.findCheckedRecord(record, checkedItems) !== -1;

            for (var i = 0; i < store.data.items.length; i++) {
                var item = store.data.items[i],
                    index = this.findCheckedRecord(item, checkedItems);

                if (allChecked && index !== -1) {
                    checkedItems.remove(checkedItems[index]);
                } else if (index === -1) {
                    checkedItems.push(item);
                }
                this.refreshItem(item);
            }
        } else {
            this.selectCommonRecord(record, checkedIndex, store, checkedItems);
        }

        if (this.checkedItems.length === 0) {
            this.disableFilterOkBtn();
        } else {
            this.activateFilterOkBtn();
        }
    },
    onSelect : function (record, checkedIndex) {
        var checkedItems = this.filterMode ? this.filterCheckedItems : this.checkedItems,
            store = this.filterMode ? this.filterStore : this.store;

        if (this.filterMode) {
            this.filterSelect(record, checkedIndex, store, checkedItems);
        } else {
            this.defaultSelect(record, checkedIndex, store, checkedItems);
        }
	},
    /**
     * Обрабатывает выбор обычной опции (все кроме Выделить все записи)
     * @param {Ext.data.Record} record
     * @param {integer} checkedIndex
     * @param {Ext.data.Store} store
     * @param {object} checkedItems
     */
    selectCommonRecord: function(record, checkedIndex, store, checkedItems) {
        var recordAll = store.getById(this.optAllId),
            index = this.findCheckedRecord(record, checkedItems);

        if (this.fireEvent("beforeselect", this, record, checkedIndex) !== false) {
            if (index === -1) {
                checkedItems.push(record);
                if (checkedItems.length === store.data.items.length - 1) {
                    checkedItems.push(recordAll);
                }
            } else {
                checkedItems.remove(checkedItems[index]);

                if (checkedItems.indexOf(recordAll) !== -1) {
                    checkedItems.remove(recordAll);
                    this.refreshItem(recordAll);
                }
            }

            this.refreshItem(record);
            this.setValue(this.getValue());
        }
    },
    getValue : function () {
		var value = [];

		Ext3.each(this.checkedItems, function (record) {
			value.push(record.eqid || record.get(this.valueField));
		}, this);

        value.remove(this.optAllId);

		return Ext3.util.JSON.encode(value);
	},
    setValue:function(v) {

        if (!v || v === '[]'){
            this.hideClearBtn();
        }
        else {
            this.showClearBtn();
        }
        this.prevValue = this.value;
        this.value = this.getValue();

        this.setRawValue(this.getText());
        if (this.hiddenField) {
            this.hiddenField.value = this.value;
        }
        if (this.el) {
            this.el.removeClass(this.emptyClass);
        }
    },
    triggerBlur: function () {
        if (this.focusClass) {
            this.el.removeClass(this.focusClass);
        }
        if (this.wrap) {
            this.wrap.removeClass(this.wrapFocusClass);
        }
        this.validate();
    }
});

Ext.reg('m3-multiselect-with-inner-filter-field', Ext.m3.MultiSelectWithInnerFilterField );
