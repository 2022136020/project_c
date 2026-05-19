import 'package:flutter/material.dart';
import '../../models/account.dart';
import '../../models/position.dart';
import '../../services/firestore_service.dart';

class AddPositionScreen extends StatefulWidget {
  final List<Account> accounts;
  const AddPositionScreen({super.key, required this.accounts});

  @override
  State<AddPositionScreen> createState() => _AddPositionScreenState();
}

class _AddPositionScreenState extends State<AddPositionScreen> {
  final _formKey = GlobalKey<FormState>();
  final _symbolController = TextEditingController();
  final _entryPriceController = TextEditingController();
  final _quantityController = TextEditingController();
  final _reasonController = TextEditingController();
  final _targetController = TextEditingController();
  final _stopLossController = TextEditingController();
  final _service = FirestoreService();

  String _assetType = 'stock';
  String? _accountId;
  DateTime _entryDate = DateTime.now();
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    if (widget.accounts.isNotEmpty) _accountId = widget.accounts.first.id;
  }

  @override
  void dispose() {
    _symbolController.dispose();
    _entryPriceController.dispose();
    _quantityController.dispose();
    _reasonController.dispose();
    _targetController.dispose();
    _stopLossController.dispose();
    super.dispose();
  }

  Future<void> _pickDate() async {
    final picked = await showDatePicker(
      context: context,
      initialDate: _entryDate,
      firstDate: DateTime(2000),
      lastDate: DateTime.now(),
    );
    if (picked != null) setState(() => _entryDate = picked);
  }

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) return;
    if (_accountId == null) {
      ScaffoldMessenger.of(context)
          .showSnackBar(const SnackBar(content: Text('계좌를 선택해 주세요.')));
      return;
    }
    setState(() => _isLoading = true);
    try {
      await _service.addPosition(Position(
        id: '',
        accountId: _accountId!,
        symbol: _symbolController.text.trim().toUpperCase(),
        assetType: _assetType,
        entryPrice: double.parse(_entryPriceController.text.replaceAll(',', '')),
        quantity: double.parse(_quantityController.text.replaceAll(',', '')),
        entryDate: _entryDate,
        entryReason: _reasonController.text.trim(),
        targetPrice: _targetController.text.isEmpty
            ? null
            : double.tryParse(_targetController.text.replaceAll(',', '')),
        stopLoss: _stopLossController.text.isEmpty
            ? null
            : double.tryParse(_stopLossController.text.replaceAll(',', '')),
        status: 'open',
      ));
      if (mounted) Navigator.pop(context);
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context)
            .showSnackBar(SnackBar(content: Text('오류: $e')));
      }
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('포지션 기록')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // 계좌 선택
              DropdownButtonFormField<String>(
                value: _accountId,
                decoration: const InputDecoration(
                  labelText: '계좌',
                  border: OutlineInputBorder(),
                ),
                items: widget.accounts
                    .map((a) => DropdownMenuItem(value: a.id, child: Text(a.name)))
                    .toList(),
                onChanged: (v) => setState(() => _accountId = v),
              ),
              const SizedBox(height: 16),
              // 자산 유형
              const Text('자산 유형', style: TextStyle(fontSize: 14, color: Colors.grey)),
              const SizedBox(height: 8),
              SegmentedButton<String>(
                segments: const [
                  ButtonSegment(value: 'stock', label: Text('주식'),
                      icon: Icon(Icons.bar_chart)),
                  ButtonSegment(value: 'coin', label: Text('코인'),
                      icon: Icon(Icons.currency_bitcoin)),
                ],
                selected: {_assetType},
                onSelectionChanged: (s) => setState(() => _assetType = s.first),
              ),
              const SizedBox(height: 16),
              // 종목명
              TextFormField(
                controller: _symbolController,
                decoration: const InputDecoration(
                  labelText: '종목명',
                  hintText: '예: 삼성전자, BTC',
                  border: OutlineInputBorder(),
                ),
                validator: (v) =>
                    (v == null || v.isEmpty) ? '종목명을 입력해 주세요.' : null,
              ),
              const SizedBox(height: 16),
              Row(children: [
                Expanded(
                  child: TextFormField(
                    controller: _entryPriceController,
                    keyboardType: TextInputType.number,
                    decoration: const InputDecoration(
                      labelText: '진입가',
                      border: OutlineInputBorder(),
                    ),
                    validator: (v) {
                      if (v == null || v.isEmpty) return '진입가를 입력해 주세요.';
                      if (double.tryParse(v.replaceAll(',', '')) == null) return '숫자만 입력';
                      return null;
                    },
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: TextFormField(
                    controller: _quantityController,
                    keyboardType: TextInputType.number,
                    decoration: const InputDecoration(
                      labelText: '수량',
                      border: OutlineInputBorder(),
                    ),
                    validator: (v) {
                      if (v == null || v.isEmpty) return '수량을 입력해 주세요.';
                      if (double.tryParse(v.replaceAll(',', '')) == null) return '숫자만 입력';
                      return null;
                    },
                  ),
                ),
              ]),
              const SizedBox(height: 16),
              // 진입일
              InkWell(
                onTap: _pickDate,
                child: InputDecorator(
                  decoration: const InputDecoration(
                    labelText: '진입일',
                    border: OutlineInputBorder(),
                    prefixIcon: Icon(Icons.calendar_today_outlined),
                  ),
                  child: Text(
                    '${_entryDate.year}.${_entryDate.month.toString().padLeft(2, '0')}.${_entryDate.day.toString().padLeft(2, '0')}',
                  ),
                ),
              ),
              const SizedBox(height: 16),
              // 매수 근거
              TextFormField(
                controller: _reasonController,
                maxLines: 3,
                decoration: const InputDecoration(
                  labelText: '매수 근거',
                  hintText: '왜 이 종목을 매수했는지 기록해 두세요.',
                  border: OutlineInputBorder(),
                ),
                validator: (v) =>
                    (v == null || v.isEmpty) ? '매수 근거를 입력해 주세요.' : null,
              ),
              const SizedBox(height: 16),
              Row(children: [
                Expanded(
                  child: TextFormField(
                    controller: _targetController,
                    keyboardType: TextInputType.number,
                    decoration: const InputDecoration(
                      labelText: '목표가 (선택)',
                      border: OutlineInputBorder(),
                    ),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: TextFormField(
                    controller: _stopLossController,
                    keyboardType: TextInputType.number,
                    decoration: const InputDecoration(
                      labelText: '손절가 (선택)',
                      border: OutlineInputBorder(),
                    ),
                  ),
                ),
              ]),
              const SizedBox(height: 32),
              FilledButton(
                onPressed: _isLoading ? null : _submit,
                style: FilledButton.styleFrom(
                    padding: const EdgeInsets.symmetric(vertical: 14)),
                child: _isLoading
                    ? const SizedBox(
                        height: 20, width: 20,
                        child: CircularProgressIndicator(strokeWidth: 2))
                    : const Text('저장', style: TextStyle(fontSize: 16)),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
