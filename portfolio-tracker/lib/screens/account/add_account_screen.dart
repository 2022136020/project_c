import 'package:flutter/material.dart';
import '../../models/account.dart';
import '../../services/firestore_service.dart';

class AddAccountScreen extends StatefulWidget {
  const AddAccountScreen({super.key});

  @override
  State<AddAccountScreen> createState() => _AddAccountScreenState();
}

class _AddAccountScreenState extends State<AddAccountScreen> {
  final _formKey = GlobalKey<FormState>();
  final _nameController = TextEditingController();
  final _balanceController = TextEditingController();
  final _service = FirestoreService();

  String _type = 'stock';
  String _currency = 'KRW';
  bool _isCustomCurrency = false;
  final _customCurrencyController = TextEditingController();
  bool _isLoading = false;

  static const _presetCurrencies = ['KRW', 'USD', 'USDT'];

  @override
  void dispose() {
    _nameController.dispose();
    _balanceController.dispose();
    _customCurrencyController.dispose();
    super.dispose();
  }

  String get _resolvedCurrency =>
      _isCustomCurrency ? _customCurrencyController.text.trim() : _currency;

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() => _isLoading = true);
    try {
      await _service.addAccount(Account(
        id: '',
        name: _nameController.text.trim(),
        type: _type,
        initialBalance: double.parse(_balanceController.text.replaceAll(',', '')),
        currency: _resolvedCurrency.isEmpty ? 'KRW' : _resolvedCurrency,
        createdAt: DateTime.now(),
      ));
      if (mounted) Navigator.pop(context);
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('오류: $e')),
        );
      }
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('계좌 등록')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              TextFormField(
                controller: _nameController,
                decoration: const InputDecoration(
                  labelText: '계좌명',
                  hintText: '예: 키움 주식 계좌',
                  border: OutlineInputBorder(),
                ),
                validator: (v) =>
                    (v == null || v.isEmpty) ? '계좌명을 입력해 주세요.' : null,
              ),
              const SizedBox(height: 16),
              const Text('계좌 유형', style: TextStyle(fontSize: 14, color: Colors.grey)),
              const SizedBox(height: 8),
              SegmentedButton<String>(
                showSelectedIcon: false,
                segments: const [
                  ButtonSegment(value: 'stock', label: Text('주식'), icon: Icon(Icons.bar_chart)),
                  ButtonSegment(value: 'coin', label: Text('코인'), icon: Icon(Icons.currency_bitcoin)),
                ],
                selected: {_type},
                onSelectionChanged: (s) => setState(() => _type = s.first),
              ),
              const SizedBox(height: 16),
              const Text('통화', style: TextStyle(fontSize: 14, color: Colors.grey)),
              const SizedBox(height: 8),
              Wrap(
                spacing: 8,
                children: [
                  ..._presetCurrencies.map((c) => ChoiceChip(
                        label: Text(c),
                        selected: !_isCustomCurrency && _currency == c,
                        onSelected: (_) => setState(() {
                          _currency = c;
                          _isCustomCurrency = false;
                        }),
                      )),
                  ChoiceChip(
                    label: const Text('기타'),
                    selected: _isCustomCurrency,
                    onSelected: (_) => setState(() => _isCustomCurrency = true),
                  ),
                ],
              ),
              if (_isCustomCurrency) ...[
                const SizedBox(height: 8),
                TextFormField(
                  controller: _customCurrencyController,
                  decoration: const InputDecoration(
                    labelText: '통화 직접 입력',
                    hintText: '예: BTC, ETH, JPY',
                    border: OutlineInputBorder(),
                  ),
                  validator: (v) {
                    if (_isCustomCurrency && (v == null || v.trim().isEmpty)) {
                      return '통화를 입력해 주세요.';
                    }
                    return null;
                  },
                ),
              ],
              const SizedBox(height: 16),
              TextFormField(
                controller: _balanceController,
                keyboardType: TextInputType.number,
                decoration: InputDecoration(
                  labelText: '초기 잔액',
                  hintText: '0',
                  border: const OutlineInputBorder(),
                  prefixIcon: const Icon(Icons.account_balance_wallet_outlined),
                  prefixText: _isCustomCurrency
                      ? (_customCurrencyController.text.trim().isEmpty ? '' : '${_customCurrencyController.text.trim()} ')
                      : (_currency == 'KRW' ? '₩ ' : _currency == 'USD' ? '\$ ' : 'USDT '),
                ),
                validator: (v) {
                  if (v == null || v.isEmpty) return '초기 잔액을 입력해 주세요.';
                  final n = double.tryParse(v.replaceAll(',', ''));
                  if (n == null || n < 0) return '올바른 금액을 입력해 주세요.';
                  return null;
                },
              ),
              const SizedBox(height: 32),
              FilledButton(
                onPressed: _isLoading ? null : _submit,
                style: FilledButton.styleFrom(
                    padding: const EdgeInsets.symmetric(vertical: 14)),
                child: _isLoading
                    ? const SizedBox(
                        height: 20, width: 20,
                        child: CircularProgressIndicator(strokeWidth: 2))
                    : const Text('등록', style: TextStyle(fontSize: 16)),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
